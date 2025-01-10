import rasterio
import matplotlib.pyplot as plt

file_path = "example/PACEPAX-AH2MAP-L1C_ER2_20240910T175007_RA.tiff"

with rasterio.open(file_path, "r") as dst:
    img_data = dst.read(1)

    plt.figure()
    plt.imshow(img_data)
    plt.colorbar()
    plt.show()
    
    print(img_data.shape)