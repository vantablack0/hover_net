import girder_client
import numpy as np
from skimage.transform import resize
from matplotlib import pylab as plt
from matplotlib.colors import ListedColormap
from histomicstk.preprocessing.color_normalization import reinhard

APIURL = 'http://candygram.neurology.emory.edu:8080/api/v1/'
SAMPLE_SLIDE_ID = "5d817f5abd4404c6b1f744bb"

gc = girder_client.GirderClient(apiUrl=APIURL)
# gc.authenticate(interactive=True)
gc.authenticate(apiKey='kri19nTIGOkWH01TbzRqfohaaDWb6kPecRqGmemb')

MAG = 1.0

# color norm. standard (from TCGA-A2-A3XS-DX1, Amgad et al, 2019)
cnorm = {
    'mu': np.array([8.74108109, -0.12440419,  0.0444982]),
    'sigma': np.array([0.6135447, 0.10989545, 0.0286032]),
}

# TCGA-A2-A3XS-DX1_xmin21421_ymin37486_.png, Amgad et al, 2019)
# for macenco (obtained using rgb_separate_stains_macenko_pca()
# and reordered such that columns are the order:
# Hamtoxylin, Eosin, Null
W_target = np.array([
    [0.5807549,  0.08314027,  0.08213795],
    [0.71681094,  0.90081588,  0.41999816],
    [0.38588316,  0.42616716, -0.90380025]
])

# visualization color map
vals = np.random.rand(256, 3)
vals[0, ...] = [0.9, 0.9, 0.9]
cMap = ListedColormap(1 - vals)

# for visualization
ymin, ymax, xmin, xmax = 1000, 1500, 2500, 3000

# for reproducibility
np.random.seed(0)

# get RGB image at a small magnification
slide_info = gc.get('item/%s/tiles' % SAMPLE_SLIDE_ID)
getStr = "/item/%s/tiles/region?left=%d&right=%d&top=%d&bottom=%d" % (
    SAMPLE_SLIDE_ID, 0, slide_info['sizeX'], 0, slide_info['sizeY']
    ) + "&magnification=%.2f" % MAG
tissue_rgb = get_image_from_htk_response(
    gc.get(getStr, jsonResp=False))

# get mask of things to ignore
thumbnail_rgb = get_slide_thumbnail(gc, SAMPLE_SLIDE_ID)
mask_out, _ = get_tissue_mask(
    thumbnail_rgb, deconvolve_first=True,
    n_thresholding_steps=1, sigma=1.5, min_size=30)
mask_out = resize(
    mask_out == 0, output_shape=tissue_rgb.shape[:2],
    order=0, preserve_range=True) == 1

imgs = np.'{DATA_DIR}/images.npy')
