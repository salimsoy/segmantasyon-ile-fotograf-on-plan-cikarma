import numpy as np
import cv2
from matplotlib import pyplot as plt
from rio_creator import RioCreator 
from pozitif_mask import PozitiveMask
from negative_mask import NegativeMask



class GrabCut:
    def __init__(self,img):
        self.img = img

    
    def main(self):
        mask = np.zeros(self.img.shape[:2],np.uint8)
        
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)
        proses_rio = RioCreator(img)
        proses_rio.rio_create()
        
        rect = proses_rio.corpped_size
        cv2.grabCut(self.img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        
        self.mask2 = np.where((mask==2) | (mask==0), 0, 1).astype('uint8')
        self.img_cut = self.img*self.mask2[:,:,np.newaxis]
        
        while True:
            cv2.imshow('Detected', self.img_cut)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('a'):
                pozitive_mask = PozitiveMask(self.img)
                negative_mask = NegativeMask(self.img_cut)
                pozitive_mask.main()
                negative_mask.main()
                mask_pozitive = pozitive_mask.mask
                mask_negative = negative_mask.mask
    
                mask[mask_pozitive == 255] = 1
                mask[mask_negative == 255] = 0
                
                mask, bgdModel, fgdModel= cv2.grabCut(self.img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

                self.mask2 = np.where((mask==2) | (mask==0), 0, 1).astype('uint8')
                self.img_cut = self.img*self.mask2[:,:,np.newaxis]

              
        
            elif key == ord('q'):
                break
    
        cv2.destroyAllWindows()

     

if __name__ == '__main__':
    img = cv2.imread('messi.jpg')
    proses = GrabCut(img)
    proses.main()
    

    
