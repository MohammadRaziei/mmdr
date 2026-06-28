use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use mermaid_rs_renderer::{render_with_options, RenderOptions};

/// Build a RenderOptions from the simple set of knobs we expose to Python.
fn build_options(
    theme: Option<&str>,
    node_spacing: Option<f32>,
    rank_spacing: Option<f32>,
    aspect_ratio: Option<(f32, f32)>,
) -> RenderOptions {
    let mut opts = match theme {
        Some("classic") | Some("default") | Some("mermaid") => RenderOptions::mermaid_default(),
        _ => RenderOptions::modern(),
    };

    if let Some(spacing) = node_spacing {
        opts = opts.with_node_spacing(spacing);
    }
    if let Some(spacing) = rank_spacing {
        opts = opts.with_rank_spacing(spacing);
    }
    if let Some((w, h)) = aspect_ratio {
        opts = opts.with_preferred_aspect_ratio_parts(w, h);
    }

    opts
}

/// Render a Mermaid diagram to an SVG string.
#[pyfunction]
#[pyo3(signature = (diagram, theme=None, node_spacing=None, rank_spacing=None, aspect_ratio=None))]
fn render(
    diagram: &str,
    theme: Option<&str>,
    node_spacing: Option<f32>,
    rank_spacing: Option<f32>,
    aspect_ratio: Option<(f32, f32)>,
) -> PyResult<String> {
    let opts = build_options(theme, node_spacing, rank_spacing, aspect_ratio);
    render_with_options(diagram, opts).map_err(|e| PyValueError::new_err(e.to_string()))
}

/// Pick the first usable font family name out of a CSS-style font list,
/// mirroring how the upstream CLI picks a font for PNG rasterization.
fn primary_font(fonts: &str) -> String {
    fonts
        .split(',')
        .map(|s| s.trim().trim_matches('"'))
        .find(|s| !s.is_empty())
        .unwrap_or("Inter")
        .to_string()
}

fn parse_hex_color(input: &str) -> Option<resvg::tiny_skia::Color> {
    let hex = input.trim().strip_prefix('#')?;
    if hex.len() != 6 {
        return None;
    }
    let r = u8::from_str_radix(&hex[0..2], 16).ok()?;
    let g = u8::from_str_radix(&hex[2..4], 16).ok()?;
    let b = u8::from_str_radix(&hex[4..6], 16).ok()?;
    Some(resvg::tiny_skia::Color::from_rgba8(r, g, b, 255))
}

/// Render a Mermaid diagram straight to PNG bytes.
#[pyfunction]
#[pyo3(signature = (diagram, theme=None, node_spacing=None, rank_spacing=None, aspect_ratio=None, width=None, height=None))]
#[allow(clippy::too_many_arguments)]
fn render_png(
    diagram: &str,
    theme: Option<&str>,
    node_spacing: Option<f32>,
    rank_spacing: Option<f32>,
    aspect_ratio: Option<(f32, f32)>,
    width: Option<f32>,
    height: Option<f32>,
) -> PyResult<Vec<u8>> {
    let opts = build_options(theme, node_spacing, rank_spacing, aspect_ratio);
    let theme_obj = opts.theme.clone();

    let svg =
        render_with_options(diagram, opts).map_err(|e| PyValueError::new_err(e.to_string()))?;

    let mut usvg_opts = usvg::Options {
        font_family: primary_font(&theme_obj.font_family),
        default_size: usvg::Size::from_wh(width.unwrap_or(800.0), height.unwrap_or(600.0))
            .unwrap_or(usvg::Size::from_wh(800.0, 600.0).unwrap()),
        ..Default::default()
    };
    usvg_opts.fontdb_mut().load_system_fonts();

    let tree = usvg::Tree::from_str(&svg, &usvg_opts)
        .map_err(|e| PyValueError::new_err(format!("failed to parse generated SVG: {e}")))?;

    let size = tree.size().to_int_size();
    let mut pixmap = resvg::tiny_skia::Pixmap::new(size.width(), size.height())
        .ok_or_else(|| PyValueError::new_err("failed to allocate output image buffer"))?;

    if let Some(color) = parse_hex_color(&theme_obj.background) {
        pixmap.fill(color);
    }

    resvg::render(
        &tree,
        resvg::tiny_skia::Transform::default(),
        &mut pixmap.as_mut(),
    );

    pixmap
        .encode_png()
        .map_err(|e| PyValueError::new_err(format!("failed to encode PNG: {e}")))
}

/// mmdr: fast native Mermaid diagram rendering, powered by Rust.
#[pymodule]
fn mmdr(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render, m)?)?;
    m.add_function(wrap_pyfunction!(render_png, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
