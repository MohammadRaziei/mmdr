use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

// ---------------------------------------------------------------------------
// Backend selector
// ---------------------------------------------------------------------------

enum Backend {
    #[cfg(feature = "backend-mermaid-rs")]
    MermaidRs,
    #[cfg(feature = "backend-merman")]
    Merman,
}

fn resolve_backend(name: Option<&str>) -> PyResult<Backend> {
    match name {
        None | Some("mermaid-rs-renderer") | Some("mermaid-rs") => {
            #[cfg(feature = "backend-mermaid-rs")]
            return Ok(Backend::MermaidRs);
            #[cfg(not(feature = "backend-mermaid-rs"))]
            return Err(PyValueError::new_err(
                "backend 'mermaid-rs-renderer' was not compiled in",
            ));
        }
        Some("merman") => {
            #[cfg(feature = "backend-merman")]
            return Ok(Backend::Merman);
            #[cfg(not(feature = "backend-merman"))]
            return Err(PyValueError::new_err(
                "backend 'merman' was not compiled in",
            ));
        }
        Some(other) => Err(PyValueError::new_err(format!(
            "unknown backend {other:?}. Available: 'mermaid-rs-renderer', 'merman'"
        ))),
    }
}

// ---------------------------------------------------------------------------
// Backend A — mermaid-rs-renderer
// ---------------------------------------------------------------------------

#[cfg(feature = "backend-mermaid-rs")]
mod mermaid_rs_backend {
    use mermaid_rs_renderer::{RenderOptions, render_with_options};
    use pyo3::exceptions::PyValueError;
    use pyo3::types::PyBytes;
    use pyo3::{Bound, Python, PyResult};

    pub fn build_options(
        theme: Option<&str>,
        node_spacing: Option<f32>,
        rank_spacing: Option<f32>,
        aspect_ratio: Option<(f32, f32)>,
    ) -> RenderOptions {
        let mut opts = match theme {
            Some("classic") | Some("mermaid") => RenderOptions::mermaid_default(),
            _ => RenderOptions::modern(),
        };
        if let Some(s) = node_spacing { opts = opts.with_node_spacing(s); }
        if let Some(s) = rank_spacing { opts = opts.with_rank_spacing(s); }
        if let Some((w, h)) = aspect_ratio { opts = opts.with_preferred_aspect_ratio_parts(w, h); }
        opts
    }

    pub fn render_svg(
        diagram: &str,
        theme: Option<&str>,
        node_spacing: Option<f32>,
        rank_spacing: Option<f32>,
        aspect_ratio: Option<(f32, f32)>,
    ) -> PyResult<String> {
        let opts = build_options(theme, node_spacing, rank_spacing, aspect_ratio);
        render_with_options(diagram, opts).map_err(|e| PyValueError::new_err(e.to_string()))
    }

    fn primary_font(fonts: &str) -> String {
        fonts
            .split(',')
            .map(|s| s.trim().trim_matches('"'))
            .find(|s| !s.is_empty())
            .unwrap_or("sans-serif")
            .to_string()
    }

    fn parse_hex_color(input: &str) -> Option<resvg::tiny_skia::Color> {
        let hex = input.trim().strip_prefix('#')?;
        if hex.len() != 6 { return None; }
        let r = u8::from_str_radix(&hex[0..2], 16).ok()?;
        let g = u8::from_str_radix(&hex[2..4], 16).ok()?;
        let b = u8::from_str_radix(&hex[4..6], 16).ok()?;
        Some(resvg::tiny_skia::Color::from_rgba8(r, g, b, 255))
    }

    pub fn render_png<'py>(
        py: Python<'py>,
        diagram: &str,
        theme: Option<&str>,
        node_spacing: Option<f32>,
        rank_spacing: Option<f32>,
        aspect_ratio: Option<(f32, f32)>,
        width: Option<f32>,
        height: Option<f32>,
    ) -> PyResult<Bound<'py, PyBytes>> {
        let opts = build_options(theme, node_spacing, rank_spacing, aspect_ratio);
        let font_family = opts.theme.font_family.clone();
        let background = opts.theme.background.clone();

        let svg = render_with_options(diagram, opts)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        let mut usvg_opts = usvg::Options {
            font_family: primary_font(&font_family),
            default_size: usvg::Size::from_wh(width.unwrap_or(800.0), height.unwrap_or(600.0))
                .unwrap_or_else(|| usvg::Size::from_wh(800.0, 600.0).unwrap()),
            ..Default::default()
        };
        usvg_opts.fontdb_mut().load_system_fonts();

        let tree = usvg::Tree::from_str(&svg, &usvg_opts)
            .map_err(|e| PyValueError::new_err(format!("failed to parse SVG: {e}")))?;

        let size = tree.size().to_int_size();
        let mut pixmap = resvg::tiny_skia::Pixmap::new(size.width(), size.height())
            .ok_or_else(|| PyValueError::new_err("failed to allocate pixmap"))?;

        if let Some(color) = parse_hex_color(&background) {
            pixmap.fill(color);
        }

        resvg::render(&tree, resvg::tiny_skia::Transform::default(), &mut pixmap.as_mut());

        let data = pixmap.encode_png()
            .map_err(|e| PyValueError::new_err(format!("failed to encode PNG: {e}")))?;

        // Use PyBytes to ensure Python receives `bytes`, not `list[int]`
        // (Vec<u8> in PyO3 0.22 converts to list[int] by default).
        Ok(PyBytes::new(py, &data))
    }
}

// ---------------------------------------------------------------------------
// Backend B — merman
// ---------------------------------------------------------------------------

#[cfg(feature = "backend-merman")]
mod merman_backend {
    use merman::render::{HeadlessRenderer, raster::RasterOptions};
    use pyo3::exceptions::PyValueError;
    use pyo3::types::PyBytes;
    use pyo3::{Bound, Python, PyResult};

    pub fn render_svg(diagram: &str) -> PyResult<String> {
        HeadlessRenderer::new()
            .render_svg_resvg_safe_sync(diagram)
            .map_err(|e| PyValueError::new_err(e.to_string()))?
            .ok_or_else(|| PyValueError::new_err(
                "merman: diagram type not recognised or input is empty",
            ))
    }

    pub fn render_png<'py>(
        py: Python<'py>,
        diagram: &str,
        width: Option<u32>,
        height: Option<u32>,
        background: Option<&str>,
        scale: Option<f32>,
    ) -> PyResult<Bound<'py, PyBytes>> {
        let mut raster = RasterOptions::default();
        if let Some(bg) = background { raster = raster.with_background(bg); }
        if let Some(s) = scale { raster = raster.with_scale(s); }
        if width.is_some() || height.is_some() {
            use merman::render::raster::{RasterFitBox, RasterSizeLimit};
            raster = raster
                .with_fit_to(RasterFitBox::new(width, height))
                .with_size_limit(RasterSizeLimit::unbounded());
        }

        let data = HeadlessRenderer::new()
            .render_png_sync(diagram, &raster)
            .map_err(|e| PyValueError::new_err(e.to_string()))?
            .ok_or_else(|| PyValueError::new_err(
                "merman: diagram type not recognised or input is empty",
            ))?;

        Ok(PyBytes::new(py, &data))
    }
}

// ---------------------------------------------------------------------------
// Python-visible functions
// ---------------------------------------------------------------------------

/// Render a Mermaid diagram to an SVG string.
#[pyfunction]
#[pyo3(signature = (
    diagram,
    backend = None,
    theme = None,
    node_spacing = None,
    rank_spacing = None,
    aspect_ratio = None,
))]
fn render(
    diagram: &str,
    backend: Option<&str>,
    theme: Option<&str>,
    node_spacing: Option<f32>,
    rank_spacing: Option<f32>,
    aspect_ratio: Option<(f32, f32)>,
) -> PyResult<String> {
    match resolve_backend(backend)? {
        #[cfg(feature = "backend-mermaid-rs")]
        Backend::MermaidRs => {
            mermaid_rs_backend::render_svg(diagram, theme, node_spacing, rank_spacing, aspect_ratio)
        }
        #[cfg(feature = "backend-merman")]
        Backend::Merman => merman_backend::render_svg(diagram),
    }
}

/// Render a Mermaid diagram to PNG bytes.
///
/// Returns Python `bytes`. Uses `PyBytes` explicitly to avoid PyO3 0.22's
/// default `Vec<u8>` → `list[int]` conversion.
#[pyfunction]
#[pyo3(signature = (
    diagram,
    backend = None,
    theme = None,
    node_spacing = None,
    rank_spacing = None,
    aspect_ratio = None,
    width = None,
    height = None,
    background = None,
    scale = None,
))]
#[allow(clippy::too_many_arguments)]
fn render_png<'py>(
    py: Python<'py>,
    diagram: &str,
    backend: Option<&str>,
    theme: Option<&str>,
    node_spacing: Option<f32>,
    rank_spacing: Option<f32>,
    aspect_ratio: Option<(f32, f32)>,
    width: Option<f32>,
    height: Option<f32>,
    background: Option<&str>,
    scale: Option<f32>,
) -> PyResult<Bound<'py, PyBytes>> {
    match resolve_backend(backend)? {
        #[cfg(feature = "backend-mermaid-rs")]
        Backend::MermaidRs => mermaid_rs_backend::render_png(
            py, diagram, theme, node_spacing, rank_spacing, aspect_ratio, width, height,
        ),
        #[cfg(feature = "backend-merman")]
        Backend::Merman => merman_backend::render_png(
            py,
            diagram,
            width.map(|w| w as u32),
            height.map(|h| h as u32),
            background,
            scale,
        ),
    }
}

/// Return the list of backends compiled into this wheel.
#[pyfunction]
fn backends() -> Vec<&'static str> {
    let mut out = Vec::new();
    #[cfg(feature = "backend-mermaid-rs")]
    out.push("mermaid-rs-renderer");
    #[cfg(feature = "backend-merman")]
    out.push("merman");
    out
}

/// _mmdr: internal Rust extension — use the `mmdr` package, not this directly.
#[pymodule]
fn _mmdr(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render, m)?)?;
    m.add_function(wrap_pyfunction!(render_png, m)?)?;
    m.add_function(wrap_pyfunction!(backends, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
