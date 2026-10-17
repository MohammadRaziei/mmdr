use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

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
// SVG rendering — each backend only produces SVG, nothing else.
// Rasterization (PNG / raw pixels) lives in Python (mmdr.Diagram, via novasvg).
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
    use merman::svg::SvgPipeline;
    use merman::{OperationControl, RenderOutput, RenderRequest, Renderer, SvgRequest};

    // The "resvg-safe" pipeline replaces HTML labels / <foreignObject> with plain
    // SVG <text>, which is what simple SVG rasterizers (novasvg) can draw.
    let request = SvgRequest {
        pipeline: Some(SvgPipeline::resvg_safe()),
        ..SvgRequest::default()
    };

    let output = Renderer::new()
        .render(RenderRequest::svg(diagram, OperationControl::new(), request))
        .map_err(|e| PyValueError::new_err(e.to_string()))?;

    match output {
        RenderOutput::Svg(Some(svg)) => Ok(svg.svg().to_owned()),
        RenderOutput::Svg(None) => Err(PyValueError::new_err(
            "merman: diagram type not recognised or input is empty",
        )),
        _ => Err(PyValueError::new_err("merman: unexpected non-SVG output")),
    }
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
    m.add_function(wrap_pyfunction!(backends, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
