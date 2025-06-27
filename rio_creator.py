import cv2

class RioCreator:
    def __init__(self, img):
        self.img = img
    

    def rio_create(self):
 
      r = cv2.selectROI("Rioyu secici", self.img)

      self.cropped_image = self.img[int(r[1]):int(r[1]+r[3]), 
                            int(r[0]):int(r[0]+r[2])]
      self.corpped_size = r
      cv2.imshow('RİO', self.cropped_image)
      cv2.waitKey(0)
      cv2.destroyAllWindows()

