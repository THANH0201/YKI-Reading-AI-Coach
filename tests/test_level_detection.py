from ai.level_detection import detect_level

article = """
Etätyö on yleistynyt Suomessa viime vuosina.
"""

print(
    detect_level(article)
)