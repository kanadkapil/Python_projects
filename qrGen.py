import qrcode

def generate_qr(data, filename="qr.png"):
  """
  This function generates a QR code and saves it as an image file.
"""
  # Create a QR code object with the desired data
  qr = qrcode.QRCode(version=1, box_size=10, border=4)
  qr.add_data(data)
  qr.make(fit=True)

  # Create an img 
  img = qr.make_image(fill_color="black", back_color="white")

  # Save the imm
  img.save(filename)

if __name__ == "__main__":
  # Get data to encode from the user
  data = input("Enter text, URL, etc: ")

  # Save
  generate_qr(data)

  print(f"Saved as: qr.png")
