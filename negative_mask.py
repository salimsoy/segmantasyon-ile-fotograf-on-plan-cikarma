import cv2
import numpy as np


class NegativeMask:
    
    def __init__(self, img):
        self.image = img
        self.height, self.width = self.image.shape[:2]
        self.mask = np.zeros((self.height, self.width), dtype=np.uint8)
        self.drawing_image = self.image.copy()
        self.drawing = False  
        self.ix, self.iy = -1, -1
        



    def draw(self, event, x, y, flags, param):
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
    
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                cv2.line(self.drawing_image, (self.ix, self.iy), (x, y), (0, 0, 255), thickness=3)
                cv2.line(self.mask, (self.ix, self.iy), (x, y), 255, thickness=3)
                self.ix, self.iy = x, y
    
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.drawing_image, (self.ix, self.iy), (x, y), (0, 0, 255), thickness=3)
            cv2.line(self.mask, (self.ix, self.iy), (x, y), 255, thickness=3)

    def main(self):

        cv2.namedWindow('Çizim')
        cv2.setMouseCallback('Çizim', self.draw)
        
        while True:
            cv2.imshow('Çizim', self.drawing_image)
            key = cv2.waitKey(1) & 0xFF
            inverted_mask = cv2.bitwise_not(self.mask)
            masked_img = cv2.bitwise_and(self.image, self.image, mask=inverted_mask)
            cv2.imshow('Maske Uygulanmış Görüntü', masked_img)
        
        
            if key == ord('m'):  # 'm' ile maske göster
                cv2.imshow('Maske', self.mask)
                masked_img = cv2.bitwise_and(self.image, self.image, mask=self.mask)
                cv2.imshow('Maske Uygulanmış Görüntü', masked_img)
        
            elif key == ord('r'):  # 'r' ile sıfırla
                self.drawing_image = self.image.copy()
                self.mask = np.zeros((self.height, self.width), dtype=np.uint8)
        
            elif key == ord('q'):  # 'q' ile çık
                break
        
        cv2.destroyAllWindows()
        

        

