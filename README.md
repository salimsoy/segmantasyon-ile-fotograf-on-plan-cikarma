# Segmantasyon İle İnteraktif Olarak Görseltedi Ön Planı Çıkarma


## Segmantasyon
Görüntü segmentasyonu, bir görüntüyü anlamlı ve anlamsal olarak homojen bölgelere ayırmayı içeren temel bir bilgisayarlı görme görevidir. 
Amaç, bir görüntünün temsilini basitleştirmek veya daha ileri analizler için daha anlamlı hale getirmektir. 
Bu segmentler genellikle görüntüdeki nesnelere veya ilgi alanlarına karşılık gelir.

## GrapCut
GrabCut, bir görüntüdeki ön plandaki nesneyi örneğin bir insan, hayvan, obje arka plandan ayırmak için kullanılan bir görüntü segmentasyon yöntemidir. 
Bu algoritma ile çalışırken kullanıcı başlangıçta kullanıcı ön plan bölgesinin etrafına bir dikdörtgen çizer. Daha sonra algoritma en iyi sonucu elde etmek için bunu yinelemeli olarak parçalara ayırır. 
İlk segmentasyonların sonucu tam doğru olmayabilir bu durumda algoritmaya resim üzerinde çizerek beyaz ile çizilenler burası ön plan olmalı demek oluyorken siyah ile çizilenler burası arka plan olmalı diye algoritmaya geri bildirimde buluruz. Algoritmada bu sayede iyileştirmeler yapar.

**Temel Mantık:**
- Kullanıcıdan görüntü alınır.
- ROI Seçimi: Kullanıcı görüntü üzerinde bir dikdörtgen seçerek, segmentasyon işleminin başlayacağı bölgeyi belirler. Bu dikdörtgen, GrabCut algoritması için ilk tahmin alanıdır.
- Seçilen dikdörtgene göre GrabCut algoritması çalıştırılır. Görüntüdeki piksel değerlerine göre arka plan ve ön plan ayrılır.
- Daha sonra kullanıcı tam olarak belirlenemeyen ön plan için düzenleme yapmak istediğinde Kullanıcı a tuşuna basarak:
- PozitiveMask sınıfıyla ön plan olduğunu düşündüğü yerleri yeşil çizgilerle işaretler `m` tusuşa basarak maskeyi görür `q` tuşu ile maskeyi sonlandırır.
- NegativeMask sınıfıyla arka plan olduğunu düşündüğü yerleri kırmızı çizgilerle işaretler `m` tusuşa basarak maskeyi görür `q` tuşu ile maskeyi sonlandırır.
- Bu çizimler, GrabCut algoritmasına daha iyi sonuç verebilmesi için maskeler olarak verilirilir.
- Kullanıcının çizdiği maskeye göre cv2.GC_INIT_WITH_MASK modunda GrabCut yeniden çalıştırılır.
- Bu sayede daha kesin ve temiz bir nesne segmentasyonu elde edilir.
- çıktı ekranda gösterilir.

**Avantajları:**
- Kullanıcı sadece kabaca bir dikdörtgen çizer ya da maske ile bazı bölgeleri işaretler, geri kalan ayrımı algoritma yapar.
- Piksel renk dağılımlarını dikkate alarak sınırlı veriyle yüksek doğruluk elde eder.
- Ön plan ve arka plan çizimiyle kullanıcı müdahalesi yapılabilir.

**Dezavantajları:**
- Objeyle arka plan çok benzer renk tonlarındaysa hatalı sonuç verebilir.
- Saç, tüy, kablolar gibi ince detaylarda sınırları net ayıramaz.
- Çıktılar genellikle sert kenarlıdır, "yumuşak geçiş" (soft mask) sunmaz.
- Tam otomatik değildir, kullanıcı girişi dikdörtgen ya da çizim zorunludur.
- Çoklu nesneleri aynı anda ayırt etmek zordur.

## Segmantasyon İle Ön Plan Çıkarımı Uygulaması
### `rio_creator.py`
- Kullanıcının fare ile görüntü üzerinde dikdörtgen bir bölge seçmesini sağlar.
- Seçilen bölgenin koordinatlarını ((x, y, w, h)) GrabCut algoritmasında başlangıç olarak kullanır.
- Seçilen bölgeyi kırpıp ekranda gösterir, böylece kullanıcı görsel geri bildirim alır.

Aşağıda RioCreator sınıfı Python kodu ve açıklamaları yer almaktadır.

```python
import cv2

class RioCreator:
    def __init__(self, img):
        self.img = img  # Ana görüntü, ROI (Region of Interest) seçimi için kaydedilir.
    
    def rio_create(self):
        # Kullanıcıdan mouse ile ROI (ilgi bölgesi) seçmesini ister.
        # r = (x, y, w, h) formatında dikdörtgen koordinatları döner.
        r = cv2.selectROI("Rioyu secici", self.img)

        # Seçilen ROI'yi görüntüden kırpar (crop işlemi).
        self.cropped_image = self.img[int(r[1]):int(r[1]+r[3]),  # y'den y+h'ye
                                      int(r[0]):int(r[0]+r[2])]  # x'den x+w'ye
        
        # Seçilen ROI'nin koordinatlarını saklar (GrabCut için kullanılacak).
        self.corpped_size = r

        # Kırpılan görüntüyü ekranda gösterir.
        cv2.imshow('RİO', self.cropped_image)
        cv2.waitKey(0)  # Kullanıcı bir tuşa basana kadar bekler.
        cv2.destroyAllWindows()  # Pencereyi kapatır.

```
### `pozitif_mask.py`
- Kullanıcının ön plan (nesne) olarak görmek istediği alanları çizmesine olanak tanır (yeşil çizgi).
- Her çizim anında maske üzerinde 255 değeri atanarak GrabCut için kesin ön plan bölgesi belirlenir.
- `m, r, q` gibi tuşlarla çizimi gösterme, sıfırlama ve çıkma işlemleri yapılabilir.

Aşağıda PozitiveMask sınıfı Python kodu ve açıklamaları yer almaktadır.

```python
import cv2
import numpy as np

class PozitiveMask:
    
    def __init__(self, img):
        self.image = img  # Giriş görüntüsü
        self.height, self.width = self.image.shape[:2]  # Görüntü boyutları
        self.mask = np.zeros((self.height, self.width), dtype=np.uint8)  # Başlangıçta tümü sıfır olan maske
        self.drawing_image = self.image.copy()  # Üzerine çizim yapılacak kopya görüntü
        self.drawing = False  # Çizim yapılıp yapılmadığını tutan bayrak
        self.ix, self.iy = -1, -1  # Başlangıç çizim koordinatları (x, y)
    
    # Mouse olaylarını işleyen fonksiyon
    def draw(self, event, x, y, flags, param):
        
        if event == cv2.EVENT_LBUTTONDOWN:  # Sol tıklama başlarsa çizim başlasın
            self.drawing = True
            self.ix, self.iy = x, y  # Başlangıç noktası

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                # Çizim yapılırken çizgiyi hem görüntüye hem maskeye uygula
                cv2.line(self.drawing_image, (self.ix, self.iy), (x, y), (0, 255, 0), thickness=3)  # Görüntüye yeşil çiz
                cv2.line(self.mask, (self.ix, self.iy), (x, y), 255, thickness=3)  # Maske üzerine beyaz çiz (ön plan)
                self.ix, self.iy = x, y  # Noktayı güncelle

        elif event == cv2.EVENT_LBUTTONUP:  # Sol tıklama bırakılırsa çizimi bitir
            self.drawing = False
            # Son çizgiyi tamamla (hem görüntü hem maske üzerine)
            cv2.line(self.drawing_image, (self.ix, self.iy), (x, y), (0, 255, 0), thickness=3)
            cv2.line(self.mask, (self.ix, self.iy), (x, y), 255, thickness=3)

    # Arayüzü başlatan fonksiyon
    def main(self):

        cv2.namedWindow('Çizim')  # Çizim yapılacak pencere
        cv2.setMouseCallback('Çizim', self.draw)  # Mouse olaylarını ilgili fonksiyona yönlendir

        while True:
            cv2.imshow('Çizim', self.drawing_image)  # Üzerine çizim yapılan görüntüyü göster
            key = cv2.waitKey(1) & 0xFF  # Tuş girişi dinle

            # Maske ile görüntüyü birleştir (sadece çizilen yerler kalır)
            self.inverted_mask = cv2.bitwise_not(self.mask)
            self.masked_img = cv2.bitwise_and(self.image, self.image, mask=self.mask)
            cv2.imshow('Maske Uygulanmış Görüntü', self.masked_img)

            if key == ord('m'):  # m tuşuna basılırsa maskeyi ve uygulanmış sonucu göster
                cv2.imshow('Maske', self.mask)
                masked_img = cv2.bitwise_and(self.image, self.image, mask=self.mask)
                cv2.imshow('Maske Uygulanmış Görüntü', masked_img)

            elif key == ord('r'):  # r tuşuna basılırsa çizimi ve maskeyi sıfırla
                self.drawing_image = self.image.copy()
                self.mask = np.zeros((self.height, self.width), dtype=np.uint8)

            elif key == ord('q'):  # q tuşuna basılırsa çık
                break

        cv2.destroyAllWindows()  # Tüm pencereleri kapat

```
### `negative_mask.py`
- Kullanıcının arka plan olarak görmek istediği alanları çizmesine izin verir (kırmızı çizgi).
- Maske üzerinde çizilen alanlar 255 değeriyle işaretlenir, bu bölgeler GrabCut için kesin arka plan olarak atanır.
- `m, r, q` gibi tuşlarla çizimi gösterme, sıfırlama ve çıkma işlemleri yapılabilir.

Aşağıda NegativeMask sınıfı Python kodu ve açıklamaları yer almaktadır.

```python
import cv2
import numpy as np

class NegativeMask:
    
    def __init__(self, img):
        self.image = img  # Giriş görüntüsü
        self.height, self.width = self.image.shape[:2]  # Görüntünün yüksekliği ve genişliği
        self.mask = np.zeros((self.height, self.width), dtype=np.uint8)  # Başlangıçta siyah (0) değerli maske
        self.drawing_image = self.image.copy()  # Üzerine çizim yapılacak görüntü kopyası
        self.drawing = False  # Çizim modunu kontrol eden bayrak
        self.ix, self.iy = -1, -1  # İlk tıklanan (başlangıç) koordinatlar
    
    # Mouse olaylarını işleyen fonksiyon
    def draw(self, event, x, y, flags, param):
        # Sol tıklama başladığında çizim başlasın
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y  # Başlangıç noktası

        # Mouse hareket ederken ve çizim açıksa, çizgi çiz
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                # Görüntüye kırmızı çizgi çiz (kullanıcıya görsel geri bildirim)
                cv2.line(self.drawing_image, (self.ix, self.iy), (x, y), (0, 0, 255), thickness=3)
                # Maskeye beyaz çizgi çiz (arka plan olarak işaretle)
                cv2.line(self.mask, (self.ix, self.iy), (x, y), 255, thickness=3)
                self.ix, self.iy = x, y  # Konumu güncelle

        # Sol tıklama bırakıldığında çizimi sonlandır
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            # Son bir çizgi daha çiz (bırakıldığında nokta kalmasın)
            cv2.line(self.drawing_image, (self.ix, self.iy), (x, y), (0, 0, 255), thickness=3)
            cv2.line(self.mask, (self.ix, self.iy), (x, y), 255, thickness=3)

    # Uygulamanın çalışmasını başlatan fonksiyon
    def main(self):
        cv2.namedWindow('Çizim')  # Pencere oluştur
        cv2.setMouseCallback('Çizim', self.draw)  # Mouse olaylarını draw fonksiyonuna bağla
        
        while True:
            cv2.imshow('Çizim', self.drawing_image)  # Üzerine çizilen görüntüyü göster
            key = cv2.waitKey(1) & 0xFF  # Klavyeden tuş yakala
            
            # Maskenin tersi alınarak, işaretlenmeyen alanlar gösterilir
            inverted_mask = cv2.bitwise_not(self.mask)
            masked_img = cv2.bitwise_and(self.image, self.image, mask=inverted_mask)
            cv2.imshow('Maske Uygulanmış Görüntü', masked_img)

            # 'm' tuşuna basılırsa maskeyi ve uygulanmış sonucu göster
            if key == ord('m'):
                cv2.imshow('Maske', self.mask)
                masked_img = cv2.bitwise_and(self.image, self.image, mask=self.mask)
                cv2.imshow('Maske Uygulanmış Görüntü', masked_img)

            # 'r' tuşuna basılırsa çizim ve maskeyi sıfırla
            elif key == ord('r'):
                self.drawing_image = self.image.copy()
                self.mask = np.zeros((self.height, self.width), dtype=np.uint8)

            # 'q' tuşuna basılırsa çık
            elif key == ord('q'):
                break

        cv2.destroyAllWindows()  # Pencereleri kapat

```
### `negative_mask.py`
- RioCreator ile seçilen alan üzerinden cv2.grabCut() algoritmasını çalıştırarak nesne segmentasyonu yapar.
- Kullanıcı `a` tuşuna bastığında, PozitiveMask ve NegativeMask ile ön ve arka plan düzeltmesi yapılmasını sağlar.
- Güncellenmiş maskeye göre segmentasyonu iyileştirir ve sonucu gerçek zamanlı olarak gösterir.

Aşağıda GrapCut sınıfı Python kodu ve açıklamaları yer almaktadır.

```python
import numpy as np
import cv2
from matplotlib import pyplot as plt
from rio_creator import RioCreator 
from pozitif_mask import PozitiveMask
from negative_mask import NegativeMask

class GrabCut:
    def __init__(self, img):
        self.img = img  # Giriş görüntüsü (renkli)
    
    def main(self):
        # Maske başlatılır (her piksel başlangıçta bilinmeyen)
        mask = np.zeros(self.img.shape[:2], np.uint8)

        # GrabCut için gerekli geçici modeller (arka plan & ön plan GMM)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)

        # Kullanıcıdan ROI (ilgi bölgesi) seçilmesini ister
        proses_rio = RioCreator(self.img)
        proses_rio.rio_create()
        rect = proses_rio.corpped_size  # Seçilen dikdörtgen ROI koordinatları

        # İlk GrabCut işlemi: Dikdörtgen (rect) ile başlatılır
        cv2.grabCut(self.img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

        # 0 ve 2 olan pikseller arka plandır, diğerleri ön plan
        self.mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

        # Ön planı renkli görüntüye uygula (arka planı siyah yap)
        self.img_cut = self.img * self.mask2[:, :, np.newaxis]

        # Etkileşimli pencere döngüsü başlatılır
        while True:
            cv2.imshow('Detected', self.img_cut)  # Mevcut sonuç gösterilir
            key = cv2.waitKey(1) & 0xFF

            if key == ord('a'):
                # 'a' tuşuna basıldığında: kullanıcıdan ön plan ve arka plan çizmesi istenir
                pozitive_mask = PozitiveMask(self.img)         # Ön plan çizim aracı
                negative_mask = NegativeMask(self.img_cut)     # Arka plan çizim aracı
                pozitive_mask.main()
                negative_mask.main()

                # Kullanıcı tarafından çizilen maskeler alınır
                mask_pozitive = pozitive_mask.mask
                mask_negative = negative_mask.mask

                # Pozitif maske 255 olan yerlere kesin ön plan ata
                mask[mask_pozitive == 255] = 1  # cv2.GC_FGD

                # Negatif maske 255 olan yerlere kesin arka plan ata
                mask[mask_negative == 255] = 0  # cv2.GC_BGD

                # GrabCut algoritması elle belirlenen maskeyle tekrar çalıştırılır
                mask, bgdModel, fgdModel = cv2.grabCut(
                    self.img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK
                )

                # Yeni maske uygulanarak görüntü tekrar güncellenir
                self.mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
                self.img_cut = self.img * self.mask2[:, :, np.newaxis]

            elif key == ord('q'):
                # 'q' tuşuna basılırsa döngüden çık
                break

        # Pencereleri kapat
        cv2.destroyAllWindows()


# Ana çalıştırma bloğu
if __name__ == '__main__':
    img = cv2.imread('messi.jpg')  # Görüntü dosyası yüklenir
    proses = GrabCut(img)          # GrabCut nesnesi oluşturulur
    proses.main()                  # İşlem başlatılır

```

## Sonuç
Bu proje, OpenCV'nin GrabCut algoritmasını kullanarak görüntü segmentasyonu işlemini hem yarı otomatik hem de kullanıcı destekli olarak gerçekleştirmektedir. Kullanıcıdan alınan ROI ve isteğe bağlı çizimler sayesinde nesneler arka plandan başarıyla ayrıştırılabilir.





