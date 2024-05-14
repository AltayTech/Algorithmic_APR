# -*- coding: utf-8 -*-
import pdfplumber
import re
import cv2
import pytesseract
# import pandas as pd
import pandas as pd

print('sdfsdfsadfsdfsa')
from wand.image import Image as WandImage
from PIL import Image, ImageDraw

pdf_path = 'assets\\test_page2.pdf'
image_path = 'assets\\4\\p-140.png'
# config parameter
number_of_option = 5
number_of_column = 2

question_margin_top = 5
question_margin_bottom = 55
question_margin_left = 5
question_margin_right = 1
input_method = 'image'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_with_coords(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape
    print(f"image_width: {image_width}")
    print(f"image_height: {image_height}")

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, )
    # Apply Gaussian blurring
    blur = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Adaptive thresholding (experiment with different block sizes and C values)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    datas = pytesseract.image_to_data(thresh, config='--psm 6')
    print(f"datas: {datas}")

    text_datas = []
    for data in datas.splitlines():
        data = data.split()
        # print(f"data: {data}")

        text_datas.append(data)
    # print(f"text_datas: {text_datas}")

    text_data = []
    text_datas.remove(text_datas[0])
    for text_datas_item in text_datas:
        if len(text_datas_item) > 11:
            text_data.append({'text': text_datas_item[11],
                              'x0': float(text_datas_item[6]),
                              'top': float(text_datas_item[7]),
                              'x1': float(text_datas_item[6]) + float(text_datas_item[8]),
                              'bottom': float(text_datas_item[7]) + float(text_datas_item[9]),
                              })
    print(f"text_data: {text_data}")

    return text_data


# def extract_text_with_coords(image_path):
#     # Read the image in grayscale mode
#     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#
#     # Preprocess the image (optional, may improve accuracy)
#     # ... (e.g., denoising, adaptive thresholding)
#
#     # Find contours (connected regions) in the image
#     _, contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     # Initialize list to store text and coordinates
#     text_with_coords = []
#
#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
#
#         # Extract the region of interest (ROI) using the bounding box coordinates
#         roi = img[y:y + h, x:x + w]
#
#         # Use Tesseract to recognize text from the ROI
#         text = pytesseract.image_to_string(roi, config='--psm 6')  # Treat the ROI as a single block of text
#
#         # Append extracted text and coordinates to the list
#         text_with_coords.append((text.strip(), x, y, x + w, y + h))
#
#     return text_with_coords


# Detect the target rectangule is in main rect or not
def is_in_the_region(mainRect, targetRect):
    in_region = False
    if (mainRect[2] - targetRect[2]) > -5 and (targetRect[0] - mainRect[0]) > -5:
        if (mainRect[3] - targetRect[3]) > -5 and (targetRect[1] - mainRect[1]) > -5:
            in_region = True
        else:
            in_region = False

    else:
        in_region = False
    return in_region


def is_in_horizontal_region(mainRect, targetRect):
    in_region = False
    if (mainRect[2] - targetRect[2]) > -5 and (targetRect[0] - mainRect[0]) > -5:
        if (mainRect[3] - targetRect[3]) > -5 and (targetRect[1] - mainRect[1]) > -5:
            in_region = True
        else:
            in_region = False

    else:
        in_region = False
    return in_region


# Detect target rect is in the right of main rect or not
def is_in_right(mainRect, targetRect):
    in_right = False

    if (targetRect[0] - mainRect[0]) > 5:

        in_right = True
    else:
        in_right = False
    return in_right


# Detect target rect is in the below of main rect or not

def is_in_blew(mainRect, targetRect):
    in_blew = False

    if (targetRect[1] - mainRect[1]) > 1:

        in_blew = True
    else:
        in_blew = False
    return in_blew


# PDF'ten metin içeriği ve metinlerin koordinatlarını çıkar
with pdfplumber.open(pdf_path) as pdf:
    detected_question_numbers_general = {}
    detect_question = {}
    all_boxes = []
    detected_options = {}
    detected_options_box = []

    if input_method == 'image':
        image = cv2.imread(image_path)
        image_height, image_width, _ = image.shape
        extracted_texts_with_coords = extract_text_with_coords(image_path)
        # print(f"extracted_texts_with_coords: {extracted_texts_with_coords}")

    else:

        pdf.open(pdf_path)
        image_width = pdf.pages[0].width
        image_height = pdf.pages[0].height

        # Döküman boyutlarını ekrana basma
        print(f"Döküman Boyutları: Genişlik: {image_width}, Yükseklik: {image_height}")

        # İlk sayfa için metin içeriği ve metinlerin koordinatlarını çıkarma
        page = pdf.pages[0]
        extracted_texts_with_coords = page.extract_words()
        # print(f"extracted_texts_with_coords: {extracted_texts_with_coords}")

    for item in extracted_texts_with_coords:
        # print(f"item index: {item}")
        detected_options = {}

        text = item['text'].strip()  # Boşlukları temizleme
        x0, y0, x1, y1 = float(item['x0']), float(item['top']), float(item['x1']), float(item['bottom'])
        all_boxes.append((x0, y0, x1, y1))

        if re.match(r"^[1-9][0-9]{0,2}\.$", text) and 1 <= int(text[:-1]) <= 120:
            # print(f"item index: {text}")

            detected_question_numbers_general[text] = (x0, y0, x1, y1)
            print(f"item detected_question_numbers_general: {detected_question_numbers_general}")

        # A, B, C, D, E seçeneklerini tespit etme
        if re.match(r"^\s?[ABCDE]\s?\)$", text):
            detected_options[text] = (x0, y0, x1, y1)
            # print(f"detected_options: {detected_options}")
            detected_options_box.append(detected_options)

    # Determine the last option item(D orE)

    if number_of_option == 4:
        last_option = 'D)'
    else:
        last_option = 'E)'

    # Determine the last option item(D or E)
    for item in detected_question_numbers_general:

        x0, y0, x1, y1 = (detected_question_numbers_general[item][0], detected_question_numbers_general[item][1],

                          image_width,
                          image_height
                          )
        detect_question[item] = (x0, y0, x1, y1)
        nextHorizontalQuestionX = x1
        nexVerticallyQuestionY = y1

        for item2 in detected_question_numbers_general:
            if is_in_right(detect_question[item], detected_question_numbers_general[item2]) and number_of_column == 2:
                nextHorizontalQuestionX = detected_question_numbers_general[item2][0] - 3
                x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                  image_width,
                                  image_height)
                detect_question[item] = (x0, y0, x1, y1)

            if is_in_the_region(detect_question[item], detected_question_numbers_general[item2]):
                # print(f"is_in_the_region: {detected_question_numbers_general[item2]}")

                detect_question[item] = (x0, y0, x1, y1)
                if not is_in_right(detect_question[item], detected_question_numbers_general[item2]):
                    if is_in_blew(detect_question[item], detected_question_numbers_general[item2]):
                        print(f"is_in_blew: {detected_question_numbers_general[item2]}")
                        nexVerticallyQuestionY = detected_question_numbers_general[item2][1] - 3
                        x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                          nextHorizontalQuestionX,
                                          nexVerticallyQuestionY)
                        detect_question[item] = (x0, y0, x1, y1)
                else:
                    nextHorizontalQuestionX = detected_question_numbers_general[item2][0] - 3
                    x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                      nextHorizontalQuestionX,
                                      nexVerticallyQuestionY)
                    detect_question[item] = (x0, y0, x1, y1)
        number_of_included_option = 0
        have_last_option = False
        for detected_options_item in detected_options_box:
            for option_item in detected_options_item:
                if is_in_the_region(detect_question[item], detected_options_item[option_item]):
                    number_of_included_option = number_of_included_option + 1
                    nexVerticallyQuestionY = detected_options_item[option_item][3]

                    if option_item == last_option:
                        nexVerticallyQuestionY = detected_options_item[option_item][3]
        x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                          nextHorizontalQuestionX,
                                          nexVerticallyQuestionY)
        detect_question[item] = (x0, y0, x1, y1)

        if number_of_included_option < 1:
            del detect_question[item]
        else:
            dis_item = 0
            selected_item = detect_question[item]
            for all_boxes_item in all_boxes:

                if is_in_the_region(detect_question[item], all_boxes_item):
                    if dis_item < all_boxes_item[2] - detect_question[item][0]:
                        dis_item = all_boxes_item[2] - detect_question[item][0]
                        selected_item = all_boxes_item
                nextHorizontalQuestionX = selected_item[2]
                x0, y0, x1, y1 = (detect_question[item][0], detect_question[item][1],
                                  nextHorizontalQuestionX,
                                  nexVerticallyQuestionY)
            detect_question[item] = (x0, y0, x1, y1)

            x0, y0, x1, y1 = (
                detect_question[item][0] - question_margin_left, detect_question[item][1] - question_margin_top,
                nextHorizontalQuestionX + question_margin_right,
                nexVerticallyQuestionY + question_margin_bottom)
            detect_question[item] = (x0, y0, x1, y1)

print(f"detected_options_box: {len(detected_options_box)}")

if input_method == 'pdf':
    # PDF'yi imaja dönüştürme
    with WandImage(filename=pdf_path, resolution=300) as source:
        images = source.sequence
        img_page_1 = WandImage(images[0])
        img_page_1_path = "converted_image_page_1.jpg"
        img_page_1.save(filename=img_page_1_path)

    # İmajı PIL ile açma ve boyutlandırma
    im = Image.open(img_page_1_path)
    resized_im = im.resize((int(pdf.pages[0].width), int(pdf.pages[0].height)))
else:
    im = Image.open(image_path)
    resized_im = im.resize((int(image_width), int(image_height)))

# Yeniden boyutlandırılmış imaj üzerine dikdörtgen çizme
draw = ImageDraw.Draw(resized_im)
for (x0, y0, x1, y1) in all_boxes:
    draw.rectangle([(x0, y0), (x1, y1)], outline="green")

for _, (x0, y0, x1, y1) in detected_question_numbers_general.items():
    draw.rectangle([(x0, y0), (x1, y1)], outline="red", width=1)
for detected_options_item in detected_options_box:
    for _, (x0, y0, x1, y1) in detected_options_item.items():
        draw.rectangle([(x0, y0), (x1, y1)], outline="blue")

for _, (x0, y0, x1, y1) in detect_question.items():
    draw.rectangle([(x0, y0), (x1, y1)], outline="red", width=3)

# İmajı kaydetme
img_with_all_boxes_resized_path = "result_image.jpg"
resized_im.save(img_with_all_boxes_resized_path)
