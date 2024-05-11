# -*- coding: utf-8 -*-
import pdfplumber
import re
import rpack

print('sdfsdfsadfsdfsa')

from wand.image import Image as WandImage
from PIL import Image, ImageDraw

pdf_path = 'D:\Area\Fernus\\reza\\reza\\test_page2.pdf'


def is_in_the_region(mainRect, targetRect):
    in_region = False
    if mainRect[0] > targetRect[0] and mainRect[2] < targetRect[2]:
        if mainRect[0] > targetRect[0] and mainRect[2] < targetRect[2]:
            in_region = True
    else:
        in_region = False
    return in_region


def is_in_right(mainRect, targetRect):
    in_right = False

    if mainRect[0] < targetRect[0]:

        in_right = True
    else:
        in_right = False
    return in_right


def is_in_blew(mainRect, targetRect):
    in_blew = False

    if mainRect[1] < targetRect[1]:

        in_blew = True
    else:
        in_blew = False
    return in_blew


# PDF'ten metin içeriği ve metinlerin koordinatlarını çıkar
with pdfplumber.open(pdf_path) as pdf:
    detected_question_numbers_general = {}
    detect_question = {}
    all_boxes = []
    detected_options = []
    pdf.open(pdf_path)

    # Döküman boyutlarını ekrana basma
    print(f"Döküman Boyutları: Genişlik: {pdf.pages[0].width}, Yükseklik: {pdf.pages[0].height}")

    # İlk sayfa için metin içeriği ve metinlerin koordinatlarını çıkarma
    page = pdf.pages[0]
    extracted_texts_with_coords = page.extract_words()

    for item in extracted_texts_with_coords:
        # print(f"item index: {item}")

        text = item['text'].strip()  # Boşlukları temizleme
        x0, y0, x1, y1 = item['x0'], item['top'], item['x1'], item['bottom']
        all_boxes.append((x0, y0, x1, y1))

        if re.match(r"^[1-9][0-9]{0,2}\.$", text) and 1 <= int(text[:-1]) <= 120:
            print(f"item index: {text}")

            detected_question_numbers_general[text] = (x0, y0, x1, y1)
            print(f"item detected_question_numbers_general: {detected_question_numbers_general[text]}")

        # A, B, C, D, E seçeneklerini tespit etme
        if re.match(r"^\s?[ABCDE]\s?\)$", text):
            detected_options.append((x0, y0, x1, y1))

    for item in detected_question_numbers_general:
        print(f"item index: {item}")
        print(f"item index: {detected_question_numbers_general[item]}")
        print(f"item index: {detected_question_numbers_general[item][0]}")

        # text = item['text'].strip()  # Boşlukları temizleme
        x0, y0, x1, y1 = (detected_question_numbers_general[item][0], detected_question_numbers_general[item][1],
                          detected_question_numbers_general[item][0] + 250,
                          detected_question_numbers_general[item][1] + 200)
        print(f"item index2: {item}")
        nextHorizontalQuestionX = x0
        nexVerticallyQuestionY = y0 + 30
        isLastVerticallyQuestion = False
        isLastHorizontallyQuestion = False

        # mindif

        # for item2 in detected_question_numbers_general:
        #     if nextHorizontalQuestionX < detected_question_numbers_general[item2][0]:
        #         nextHorizontalQuestionX = detected_question_numbers_general[item2][0]
        #
        #     if nexVerticallyQuestionY < detected_question_numbers_general[item2][3]:
        #         nexVerticallyQuestionY = detected_question_numbers_general[item2][3]

        # x0, y0, x1, y1 = (detected_question_numbers_general[item][0], detected_question_numbers_general[item][1],
        #                   nextHorizontalQuestionX,
        #                   nexVerticallyQuestionY)
        detect_question[item] = (x0, y0, x1, y1)

# PDF'yi imaja dönüştürme
with WandImage(filename=pdf_path, resolution=300) as source:
    images = source.sequence
    img_page_1 = WandImage(images[0])
    img_page_1_path = "converted_image_page_1.jpg"
    img_page_1.save(filename=img_page_1_path)

# İmajı PIL ile açma ve boyutlandırma
im = Image.open(img_page_1_path)
resized_im = im.resize((int(pdf.pages[0].width), int(pdf.pages[0].height)))

# Yeniden boyutlandırılmış imaj üzerine dikdörtgen çizme
draw = ImageDraw.Draw(resized_im)
for (x0, y0, x1, y1) in all_boxes:
    draw.rectangle([(x0, y0), (x1, y1)], outline="green")

for _, (x0, y0, x1, y1) in detected_question_numbers_general.items():
    draw.rectangle([(x0, y0), (x1, y1)], outline="red")

for (x0, y0, x1, y1) in detected_options:
    draw.rectangle([(x0, y0), (x1, y1)], outline="blue")

for _, (x0, y0, x1, y1) in detect_question.items():
    draw.rectangle([(x0, y0), (x1, y1)], outline="red")

# İmajı kaydetme
img_with_all_boxes_resized_path = "image_with_all_boxes_resized.jpg"
resized_im.save(img_with_all_boxes_resized_path)
