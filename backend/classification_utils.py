from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf, config
import subprocess
import tempfile
import ezdxf
from cairosvg import svg2png


async def svg_to_png(svg_byte: bytes) -> bytes:
    """Convertit un fichier SVG en PNG avec ImageMagick."""
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_temp:
        svg_temp.write(svg_byte)
        svg_temp.flush()

        png_temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        png_temp.close()

        subprocess.run(["magick", svg_temp.name, png_temp.name], check=True)

        with open(png_temp.name, "rb") as png_file:
            png_data = png_file.read()

    return png_data


async def cairosvg(svg_bytes: bytes) -> bytes:
    """Convertit un fichier SVG en PNG avec CairoSVG."""
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_temp:
        svg_temp.write(svg_bytes)
        svg_temp.flush()

        png_temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        png_temp.close()

        svg2png(url=svg_temp.name, write_to=png_temp.name, background_color="white")

        with open(png_temp.name, "rb") as png_file:
            png_data = png_file.read()

    return png_data


async def dxf_to_png(dxf_bytes: bytes) -> bytes:
    """Convertit un fichier DXF en PNG."""
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as dxf_temp:
        dxf_temp.write(dxf_bytes)
        dxf_temp.flush()

        # 0. read the DXF file
        doc = ezdxf.readfile(dxf_temp.name)
        msp = doc.modelspace()
        # 1. create the render context
        context = RenderContext(doc)
        # 2. create the backend
        backend = pymupdf.PyMuPdfBackend()
        # 2.1 Create a new configuration for a white background and a black foreground color
        cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE)
        # 3. create the frontend
        frontend = Frontend(context, backend, config=cfg)
        # 4. draw the modelspace
        frontend.draw_layout(msp)
        # 5. create an A4 page layout, not required for all backends
        # the page size is auto detect by setting width and/or height to 0
        # A4 is 210x297 mm
        page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        # 6. get the PNG rendering as bytes

        # Create a temporary file to save the PNG
        png_temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        png_temp.close()

        # get the PNG rendering as bytes
        png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=96)

        # Save the PNG bytes to the temporary file
        with open(png_temp.name, "wb") as fp:
            fp.write(png_bytes)

        return png_bytes
