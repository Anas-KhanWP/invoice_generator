from PIL import Image

# Open an existing image
image = Image.open("images/logo.png")

# Convert to a non-interlaced PNG
image.save("logo_non_interlaced.png", format="PNG", interlace=False)

# Optionally, resize the image to a smaller size
image = image.resize((300, 200))  # Adjust the size as needed
image.save("logo_resized.png", format="PNG", interlace=False)
