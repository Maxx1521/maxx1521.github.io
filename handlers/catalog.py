from linebot.v3.messaging import (
    FlexMessage, FlexContainer, TextMessage,
)

CATEGORY_META = {
    "海島型實木地板": {
        "image": "https://images.unsplash.com/photo-1567225557594-88d73e55f2cb?w=800",
        "price_from": "NT$ 9,350",
    },
    "超耐磨木地板": {
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
        "price_from": "NT$ 3,700",
    },
    "石塑地板": {
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "price_from": "NT$ 3,250",
    },
    "塑膠地磚": {
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
        "price_from": "NT$ 2,300",
    },
    "戶外塑木地板": {
        "image": "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800",
        "price_from": "洽詢門市",
    },
}

CATEGORY_ORDER = ["海島型實木地板", "超耐磨木地板", "石塑地板", "塑膠地磚", "戶外塑木地板"]

# 超耐磨木地板：品牌 → 款式
LAMINATE_BRANDS = {
    "山井富士山": {
        "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sanwell_logo_card.jpg",
        "desc": "抗水白基材 24小時防水滲、日系獨家花色",
        "products": [
            {
                "name": "典藏款",
                "desc": "9.5mm｜抗水超耐磨｜日系花色設計",
                "price": "NT$ 3,700/坪",
                "colors": [
                    {"name": "宮崎白梣", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_miyazaki.jpg"},
                    {"name": "富山白橡", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_tomiyama.jpg"},
                    {"name": "千葉秋香", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_chiba.jpg"},
                    {"name": "佐賀榆木", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_saga.jpg"},
                    {"name": "京都淺橡", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_kyoto.jpg"},
                    {"name": "奈良灰橡", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_nara.jpg"},
                    {"name": "長野檜木", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_nagano.jpg"},
                    {"name": "熊本橡木", "image": "https://raw.githubusercontent.com/Maxx1521/south-home-linebot/master/assets/sw_kumamoto.jpg"},
                ],
                "url": "https://shengyang1688.com/portfolio-item/%E5%B1%B1%E4%BA%95%E5%8D%A1%E6%89%A3%E8%B6%85%E8%80%90%E7%A3%A89-5mm/",
            },
            {
                "name": "尊爵款",
                "desc": "13.5mm｜頂級厚實踏感｜精選花色",
                "price": "NT$ 4,250/坪",
                "colors": [
                    {"name": "高知橡木", "image": "https://shengyang1688.com/wp-content/uploads/2025/07/%E9%AB%98%E7%9F%A5%E6%A9%A1%E6%9C%A8-1.jpg"},
                    {"name": "姬路白橡", "image": "https://shengyang1688.com/wp-content/uploads/2025/07/%E5%A7%AC%E8%B7%AF%E7%99%BD%E6%A9%A1.jpg"},
                    {"name": "銀山淺橡", "image": "https://shengyang1688.com/wp-content/uploads/2025/07/%E9%8A%80%E5%B1%B1%E6%B7%BA%E6%A9%A1-1.jpg"},
                    {"name": "慕尼黑", "image": "https://shengyang1688.com/wp-content/uploads/2025/07/%E6%85%95%E5%B0%BC%E9%BB%91-1.jpg"},
                ],
                "url": "https://shengyang1688.com/portfolio-item/%E5%B1%B1%E4%BA%95%E5%8D%A1%E6%89%A3%E8%B6%85%E8%80%90%E7%A3%A813-5mm/",
            },
        ],
    },
    "派斯吐司倒角": {
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
        "products": [
            {"name": "派斯吐司倒角系列", "desc": "比利時Panstone設計，獨創吐司倒角圓潤邊緣，防刮耐磨22000轉，北歐風格", "price": "NT$ 4,500/坪"},
        ],
    },
    "森WoodLand": {
        "image": "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800",
        "products": [
            {"name": "一般款", "desc": "頂級AC5耐磨等級，12mm厚寬板，防潮防變形，同步紋理質感到位", "price": "NT$ 5,200/坪"},
            {"name": "人字拼", "desc": "AC5等級人字拼設計，寬厚木板踏感扎實，顏色漂亮細節質感升級", "price": "NT$ 7,100/坪"},
        ],
    },
    "Krono畢卡索": {
        "image": "https://images.unsplash.com/photo-1580237541049-2d715a09486e?w=800",
        "products": [
            {"name": "寬長款", "desc": "德國製AC5耐磨認證，4V導角設計，降噪19dB，卡扣安裝省時快速", "price": "NT$ 6,800/坪"},
            {"name": "人字拼", "desc": "德國原廠製造，人字拼設計厚實腳感，4V導角結構堅固防潮性強", "price": "NT$ 7,500/坪"},
        ],
    },
    "德國EGGER": {
        "image": "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=800",
        "products": [
            {"name": "黃標", "desc": "德國製造品質卓越，環保認證，表面耐磨易清潔，多樣花色選擇", "price": "NT$ 4,300/坪"},
            {"name": "紅標", "desc": "德國進口高級系列，抗潮性能業界最高，低甲醛綠建材標章認證", "price": "NT$ 5,100/坪"},
            {"name": "綠標", "desc": "德國原裝進口，耐磨等級AC4商用級，花色豐富適合各種風格", "price": "NT$ 5,500/坪"},
            {"name": "藍標", "desc": "德國藍天使標章認證，防潮抗水性能卓越，細緻木紋質感真實", "price": "NT$ 5,900/坪"},
            {"name": "人字拼", "desc": "源自16世紀歐洲工藝，卡扣系統拼裝快速，表面耐磨好保養", "price": "NT$ 7,300/坪"},
        ],
    },
    "羅賓地板": {
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
        "products": [
            {"name": "羅賓地板", "desc": "馬來西亞熱帶硬木製造，AC4耐磨商用等級，超耐潮防白蟻十年保證", "price": "NT$ 3,700/坪"},
        ],
    },
    "都華地板": {
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
        "products": [
            {"name": "都華地板", "desc": "韓國Dongwha品牌，Class 32商用等級耐磨，Uniclic卡扣安裝無需上膠", "price": "NT$ 3,700/坪"},
        ],
    },
}

# 其他分類：直接列商品
PRODUCTS = {
    "海島型實木地板": [
        {
            "name": "Ua雙橡園",
            "desc": "MIT台灣製，瑞典卡扣技術，北美白橡木表層，穩定耐潮，安裝快速省工",
            "price": "NT$ 9,350~12,300/坪",
            "image": "https://images.unsplash.com/photo-1567225557594-88d73e55f2cb?w=800",
        },
    ],
    "石塑地板": [
        {"name": "愛麗絲 法國系列", "desc": "6.5mm卡扣石塑地板，雙層結構穩定耐用，木紋重複率低質感細緻", "price": "NT$ 3,250/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "愛麗絲 英倫系列", "desc": "英式風格石塑地板，防水零甲醛，雙板膜工藝細節處理精緻", "price": "NT$ 3,700/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "派斯 石紋", "desc": "比利時設計吐司倒角SPC，深淺石紋選擇，防水零醛好安心易清潔", "price": "NT$ 4,500/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "派斯 木紋", "desc": "派斯SPC木紋款，吐司倒角業界首創不卡溝，多色搭配好選擇", "price": "NT$ 4,500/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "酷石 石紋S系列", "desc": "SPC卡扣地板，石紋紋理細膩層次感強，耐磨層加厚使用年限加倍", "price": "NT$ 3,900/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "酷石 水磨石W系列", "desc": "水磨石美感低調耐看，全同色配件無色差問題，防水防黴高耐用", "price": "NT$ 4,200/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "酷石 歐洲EU系列", "desc": "歐洲經典花色，防水防黴抗汙降噪，CP值高適合全室鋪設", "price": "NT$ 3,900/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "酷石 歐洲EU人字拼", "desc": "EU系列人字拼設計，立體視覺延伸感強，防水防潮適合濕熱氣候", "price": "NT$ 5,700/坪", "image": "https://images.unsplash.com/photo-1580237541049-2d715a09486e?w=800"},
        {"name": "酷石 微水泥系列", "desc": "微水泥風格SPC地板，低調質感耐看，現代設計好清潔維護簡單", "price": "NT$ 6,000/坪", "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"},
        {"name": "寶陞 人字拼", "desc": "高抗水12mm人字拼，Dura Shield抗刮防汙塗層，創意革新設計", "price": "NT$ 6,500/坪", "image": "https://images.unsplash.com/photo-1580237541049-2d715a09486e?w=800"},
    ],
    "塑膠地磚": [
        {"name": "石系列", "desc": "PVC塑膠地磚石紋款，高解析石紋圖層紋路細膩，無須打蠟維護簡單", "price": "NT$ 2,300/坪", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800"},
        {"name": "樹系列", "desc": "PVC塑膠地磚木紋款，溫潤木質表現，多層複合結構穩定耐用防潮", "price": "NT$ 2,300/坪", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800"},
    ],
    "戶外塑木地板": [],
}


def _product_bubble(p, product_key):
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": p["image"],
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": p["name"], "weight": "bold", "size": "md"},
                {"type": "text", "text": p["desc"], "size": "sm", "color": "#666666", "margin": "sm", "wrap": True},
                {"type": "text", "text": p["price"], "size": "sm", "color": "#4CAF50", "margin": "md", "weight": "bold"},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#5C8D5E",
                    "action": {
                        "type": "postback",
                        "label": "預約到府丈量",
                        "data": f"action=booking&product={product_key}",
                    },
                }
            ],
        },
    }


NOTION_CATEGORY_URLS = {
    "超耐磨木地板": "https://maxx1521.github.io",
    "石塑地板": "https://maxx1521.github.io",
    "海島型實木地板": "https://maxx1521.github.io",
    "塑膠地磚": "https://maxx1521.github.io",
    "戶外塑木地板": "https://maxx1521.github.io",
}


def get_category_flex():
    bubbles = []
    for category in CATEGORY_ORDER:
        meta = CATEGORY_META[category]
        if category == "超耐磨木地板":
            count_text = f"{len(LAMINATE_BRANDS)} 個品牌"
        elif not PRODUCTS.get(category):
            count_text = "敬請期待"
        else:
            count_text = f"{len(PRODUCTS[category])} 款商品"

        notion_url = NOTION_CATEGORY_URLS.get(category, "https://www.notion.so/2fc5ab351ee5801a8800c8f3c9e4b905")

        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": meta["image"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": category, "weight": "bold", "size": "lg"},
                    {"type": "text", "text": count_text, "size": "sm", "color": "#888888", "margin": "sm"},
                    {"type": "text", "text": f"從 {meta['price_from']}", "size": "sm", "color": "#4CAF50", "margin": "sm"},
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#5C8D5E",
                        "action": {
                            "type": "uri",
                            "label": "查看完整系列",
                            "uri": notion_url,
                        },
                    }
                ],
            },
        }
        bubbles.append(bubble)

    carousel = {"type": "carousel", "contents": bubbles}
    return FlexMessage(alt_text="產品目錄", contents=FlexContainer.from_dict(carousel))


def get_products_flex(category):
    if category == "超耐磨木地板":
        return _laminate_brands_flex()

    products = PRODUCTS.get(category, [])
    if not products:
        return TextMessage(text="此分類商品即將上架，歡迎來電或到門市詢問！")

    bubbles = [_product_bubble(p, p["name"]) for p in products]
    carousel = {"type": "carousel", "contents": bubbles}
    return FlexMessage(alt_text=f"{category} 商品列表", contents=FlexContainer.from_dict(carousel))


def _laminate_brands_flex():
    bubbles = []
    for brand, info in LAMINATE_BRANDS.items():
        prices = [p["price"] for p in info["products"]]
        price_text = prices[0] if len(prices) == 1 else f"{prices[0].split('/')[0]} 起"
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": info["image"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": brand, "weight": "bold", "size": "md"},
                    {"type": "text", "text": price_text, "size": "sm", "color": "#4CAF50", "margin": "sm"},
                    *([{"type": "text", "text": info["desc"], "size": "sm", "color": "#666666", "margin": "sm", "wrap": True}] if info.get("desc") else []),
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#5C8D5E",
                        "action": {
                            "type": "postback",
                            "label": "查看款式",
                            "data": f"action=view_brand&brand={brand}",
                        },
                    }
                ],
            },
        }
        bubbles.append(bubble)

    carousel = {"type": "carousel", "contents": bubbles}
    return FlexMessage(alt_text="超耐磨木地板品牌", contents=FlexContainer.from_dict(carousel))


def get_brand_products_flex(brand):
    info = LAMINATE_BRANDS.get(brand)
    if not info:
        return TextMessage(text="找不到此品牌，請重新選擇。")

    bubbles = []
    for p in info["products"]:
        has_colors = bool(p.get("colors"))
        footer_buttons = []
        if has_colors:
            footer_buttons.append({
                "type": "button",
                "style": "primary",
                "color": "#5C8D5E",
                "action": {
                    "type": "postback",
                    "label": "查看花色",
                    "data": f"action=view_colors&brand={brand}&product={p['name']}",
                },
            })
        else:
            footer_buttons.append({
                "type": "button",
                "style": "primary",
                "color": "#5C8D5E",
                "action": {
                    "type": "postback",
                    "label": "預約到府丈量",
                    "data": f"action=booking&product={brand} {p['name']}",
                },
            })

        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": info["image"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": brand, "size": "sm", "color": "#888888"},
                    {"type": "text", "text": p["name"], "weight": "bold", "size": "md", "margin": "sm"},
                    {"type": "text", "text": p["desc"], "size": "sm", "color": "#666666", "margin": "sm", "wrap": True},
                    {"type": "text", "text": p["price"], "size": "sm", "color": "#4CAF50", "margin": "md", "weight": "bold"},
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": footer_buttons,
            },
        }
        bubbles.append(bubble)

    carousel = {"type": "carousel", "contents": bubbles}
    return FlexMessage(alt_text=f"{brand} 款式", contents=FlexContainer.from_dict(carousel))


def get_product_colors(brand, product_name):
    info = LAMINATE_BRANDS.get(brand)
    if not info:
        return TextMessage(text="找不到此品牌。")
    product = next((p for p in info["products"] if p["name"] == product_name), None)
    if not product or not product.get("colors"):
        return TextMessage(text="此款式花色資料尚未建立，歡迎來門市看實品！")

    colors = product["colors"]
    colors_text = "・".join(c["name"] if isinstance(c, dict) else c for c in colors)
    url = product.get("url")

    footer_buttons = []
    if url:
        footer_buttons.append({
            "type": "button",
            "style": "primary",
            "color": "#5C8D5E",
            "action": {"type": "uri", "label": "查看完整花色圖鑑", "uri": url},
        })

    bubbles = []
    for color in colors:
        color_name = color["name"] if isinstance(color, dict) else color
        color_img = color["image"] if isinstance(color, dict) else info["image"]
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": color_img,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": brand, "size": "sm", "color": "#888888"},
                    {"type": "text", "text": product_name, "weight": "bold", "size": "md", "margin": "sm"},
                    {"type": "text", "text": color_name, "weight": "bold", "size": "lg", "color": "#333333", "margin": "sm"},
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": footer_buttons,
            } if footer_buttons else None,
        }
        if not footer_buttons:
            bubble.pop("footer")
        bubbles.append(bubble)

    carousel = {"type": "carousel", "contents": bubbles}
    return FlexMessage(alt_text=f"{brand} {product_name} 花色", contents=FlexContainer.from_dict(carousel))
