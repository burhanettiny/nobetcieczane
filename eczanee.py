import streamlit as st
import requests

def get_pharmacies(city, district):
    url = f"https://api.https://www.eczaneler.gen.tr/{city}/{district}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

st.title("Nöbetçi Eczane Bulucu")

cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]  # Örnek şehir listesi
city = st.selectbox("Şehir seçiniz:", cities)

districts = {  # Örnek ilçe listesi
    "İstanbul": ["Kadıköy", "Beşiktaş", "Şişli"],
    "Ankara": ["Çankaya", "Keçiören", "Mamak"],
    "İzmir": ["Konak", "Bornova", "Karşıyaka"],
    "Bursa": ["Osmangazi", "Nilüfer", "Yıldırım"],
    "Antalya": ["Muratpaşa", "Kepez", "Konyaaltı"]
}

district = st.selectbox("İlçe seçiniz:", districts.get(city, []))

if st.button("Eczaneleri Listele"):
    if city and district:
        pharmacies = get_pharmacies(city, district)
        if pharmacies:
            for pharmacy in pharmacies:
                st.subheader(pharmacy['name'])
                st.write(f"Adres: {pharmacy['address']}")
                st.write(f"Telefon: {pharmacy['phone']}")
                st.map([[pharmacy['latitude'], pharmacy['longitude']]])
        else:
            st.error("Eczane bilgileri alınamadı, lütfen tekrar deneyin.")
    else:
        st.warning("Lütfen bir şehir ve ilçe seçiniz.")
