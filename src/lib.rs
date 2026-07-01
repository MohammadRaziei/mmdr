use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use resvg::tiny_skia;

// ---------------------------------------------------------------------------
// Backend selector — default is merman
// ---------------------------------------------------------------------------

enum Backend {
    #[cfg(feature = "backend-merman")]
    Merman,
    #[cfg(feature = "backend-mermaid-rs")]
    MermaidRs,
}

fn resolve_backend(name: Option<&str>) -> PyResult<Backend> {
    match name {
        // default
        None | Some("merman") => {
            #[cfg(feature = "backend-merman")]
            return Ok(Backend::Merman);
            #[cfg(not(feature = "backend-merman"))]
            return Err(PyValueError::new_err(
                "backend 'merman' is not compiled in; pass backend='mermaid-rs-renderer' or rebuild with the backend-merman feature",
            ));
        }
        Some("mermaid-rs-renderer") | Some("mermaid-rs") => {
            #[cfg(feature = "backend-mermaid-rs")]
            return Ok(Backend::MermaidRs);
            #[cfg(not(feature = "backend-mermaid-rs"))]
            return Err(PyValueError::new_err(
                "backend 'mermaid-rs-renderer' is not compiled in",
            ));
        }
        Some(other) => Err(PyValueError::new_err(format!(
            "unknown backend {other:?}. Available: 'merman' (default), 'mermaid-rs-renderer'"
        ))),
    }
}

// ---------------------------------------------------------------------------
// SVG rendering — each backend only produces SVG, nothing else
// ---------------------------------------------------------------------------

#[cfg(feature = "backend-mermaid-rs")]
fn render_svg_mermaid_rs(
    diagram: &str,
    theme: Option<&str>,
    node_spacing: Option<f32>,
    rank_spacing: Option<f32>,
    aspect_ratio: Option<(f32, f32)>,
) -> PyResult<String> {
    use mermaid_rs_renderer::{RenderOptions, render_with_options};

    let mut opts = match theme {
        Some("classic") | Some("mermaid") => RenderOptions::mermaid_default(),
        _ => RenderOptions::modern(),
    };
    if let Some(s) = node_spacing    { opts = opts.with_node_spacing(s); }
    if let Some(s) = rank_spacing    { opts = opts.with_rank_spacing(s); }
    if let Some((w, h)) = aspect_ratio { opts = opts.with_preferred_aspect_ratio_parts(w, h); }

    render_with_options(diagram, opts).map_err(|e| PyValueError::new_err(e.to_string()))
}

#[cfg(feature = "backend-merman")]
fn render_svg_merman(diagram: &str) -> PyResult<String> {
    use merman::render::HeadlessRenderer;

    HeadlessRenderer::new()
        .render_svg_resvg_safe_sync(diagram)
        .map_err(|e| PyValueError::new_err(e.to_string()))?
        .ok_or_else(|| PyValueError::new_err(
            "merman: diagram type not recognised or input is empty",
        ))
}

// ---------------------------------------------------------------------------
// Rasterization helpers — always uses resvg, independent of backend
// ---------------------------------------------------------------------------

fn parse_hex_color(css: &str) -> Option<tiny_skia::Color> {
    let hex = css.trim().strip_prefix('#')?;
    if hex.len() != 6 { return None; }
    let r = u8::from_str_radix(&hex[0..2], 16).ok()?;
    let g = u8::from_str_radix(&hex[2..4], 16).ok()?;
    let b = u8::from_str_radix(&hex[4..6], 16).ok()?;
    Some(tiny_skia::Color::from_rgba8(r, g, b, 255))
}

/// Parse and rasterize an SVG string into a tiny-skia Pixmap (raw RGBA8888).
/// background: optional CSS hex color to fill before rendering (e.g. "#ffffff").
fn svg_to_pixmap(
    svg: &str,
    width: Option<f32>,
    height: Option<f32>,
    background: Option<&str>,
) -> PyResult<tiny_skia::Pixmap> {
    let mut opts = usvg::Options {
        default_size: usvg::Size::from_wh(
            width.unwrap_or(800.0),
            height.unwrap_or(600.0),
        )
        .unwrap_or_else(|| usvg::Size::from_wh(800.0, 600.0).unwrap()),
        ..Default::default()
    };
    opts.fontdb_mut().load_system_fonts();

    let tree = usvg::Tree::from_str(svg, &opts)
        .map_err(|e| PyValueError::new_err(format!("SVG parse error: {e}")))?;

    let size = tree.size().to_int_size();
    let mut pixmap = tiny_skia::Pixmap::new(size.width(), size.height())
        .ok_or_else(|| PyValueError::new_err("failed to allocate pixmap"))?;

    if let Some(color) = background.and_then(parse_hex_color) {
        pixmap.fill(color);
    }

    resvg::render(&tree, tiny_skia::Transform::default(), &mut pixmap.as_mut());
    Ok(pixmap)
}

// ---------------------------------------------------------------------------
// Public Python API
// ---------------------------------------------------------------------------

/// Render a Mermaid diagram to an SVG string.
///
/// Args:
///   diagram:      Mermaid source text.
///   backend:      ``"merman"`` (default) or ``"mermaid-rs-renderer"``.
///
///   mermaid-rs-renderer only:
///     theme ("modern" | "classic"), node_spacing, rank_spacing, aspect_ratio
#[pyfunction]
#[pyo3(signature = (
    diagram,
    backend      = None,
    theme        = None,
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
        #[cfg(feature = "backend-merman")]
        Backend::Merman => render_svg_merman(diagram),

        #[cfg(feature = "backend-mermaid-rs")]
        Backend::MermaidRs => {
            render_svg_mermaid_rs(diagram, theme, node_spacing, rank_spacing, aspect_ratio)
        }
    }
}

/// Convert an SVG string to PNG bytes using resvg.
///
/// This is backend-agnostic: pass the SVG string you got from ``render()``.
///
/// Args:
///   svg:        SVG source text.
///   width:      Canvas width hint in pixels (default 800).
///   height:     Canvas height hint in pixels (default 600).
///   background: Background fill color as a CSS hex string (e.g. ``"#ffffff"``).
///               Transparent by default.
#[pyfunction]
#[pyo3(signature = (svg, width = None, height = None, background = None))]
fn svg_to_png<'py>(
    py: Python<'py>,
    svg: &str,
    width: Option<f32>,
    height: Option<f32>,
    background: Option<&str>,
) -> PyResult<Bound<'py, PyBytes>> {
    let pixmap = svg_to_pixmap(svg, width, height, background)?;
    let encoded = pixmap.encode_png()
        .map_err(|e| PyValueError::new_err(format!("PNG encode error: {e}")))?;
    Ok(PyBytes::new_bound(py, &encoded))
}

/// Convert an SVG string to raw RGBA8888 pixel data using resvg.
///
/// Returns ``(raw_bytes, width, height)`` — the raw bytes have stride
/// ``width * 4`` and are laid out row-by-row, top to bottom.
/// Use with numpy: ``np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)``
///
/// Args:
///   svg:        SVG source text.
///   width:      Canvas width hint in pixels (default 800).
///   height:     Canvas height hint in pixels (default 600).
///   background: Background fill color as a CSS hex string (e.g. ``"#ffffff"``).
#[pyfunction]
#[pyo3(signature = (svg, width = None, height = None, background = None))]
fn svg_to_raw<'py>(
    py: Python<'py>,
    svg: &str,
    width: Option<f32>,
    height: Option<f32>,
    background: Option<&str>,
) -> PyResult<(Bound<'py, PyBytes>, u32, u32)> {
    let pixmap = svg_to_pixmap(svg, width, height, background)?;
    let w = pixmap.width();
    let h = pixmap.height();
    let raw = PyBytes::new_bound(py, pixmap.data());
    Ok((raw, w, h))
}

/// Return the list of SVG backends compiled into this wheel.
#[pyfunction]
fn backends() -> Vec<&'static str> {
    let mut out = Vec::new();
    #[cfg(feature = "backend-merman")]
    out.push("merman");
    #[cfg(feature = "backend-mermaid-rs")]
    out.push("mermaid-rs-renderer");
    out
}

/// _mmdr internal Rust extension.  Use the ``mmdr`` package directly.
#[pymodule]
fn _mmdr(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render, m)?)?;
    m.add_function(wrap_pyfunction!(svg_to_png, m)?)?;
    m.add_function(wrap_pyfunction!(svg_to_raw, m)?)?;
    m.add_function(wrap_pyfunction!(backends, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
