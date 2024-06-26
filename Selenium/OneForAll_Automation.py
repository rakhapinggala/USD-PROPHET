from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import csv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor


# Fungsi untuk mengunduh data kurs USD
def Get_USD(access_type, currency, start_date, end_date_fix, file_name):

    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        # print("Membuka URL untuk USD...")
        driver.get(
            "https://www.bi.go.id/id/statistik/informasi-kurs/transaksi-bi/default.aspx"
        )

        wait = WebDriverWait(driver, 5)

        # print("Memilih akses data...")
        access_data_dropdown = Select(
            wait.until(EC.element_to_be_clickable((By.ID, "selectPeriod")))
        )
        access_data_dropdown.select_by_visible_text(access_type)

        # print("Memilih mata uang...")
        currency_dropdown = Select(
            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.ID,
                        "ctl00_PlaceHolderMain_g_6c89d4ad_107f_437d_bd54_8fda17b556bf_ctl00_ddlmatauang1",
                    )
                )
            )
        )
        currency_dropdown.select_by_visible_text(currency)

        # print("Mengatur tanggal...")
        start_date_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_PlaceHolderMain_g_6c89d4ad_107f_437d_bd54_8fda17b556bf_ctl00_txtFrom",
                )
            )
        )
        start_date_input.clear()
        start_date_input.send_keys(start_date.strftime("%d-%m-%Y"))

        end_date_input = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_PlaceHolderMain_g_6c89d4ad_107f_437d_bd54_8fda17b556bf_ctl00_txtTo",
                )
            )
        )
        end_date_input.clear()
        end_date_input.send_keys(end_date_fix.strftime("%d-%m-%Y"))

        # print("Mengklik tombol pencarian...")
        search_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.NAME,
                    "ctl00$PlaceHolderMain$g_6c89d4ad_107f_437d_bd54_8fda17b556bf$ctl00$btnSearch1",
                )
            )
        )
        search_button.click()

        # print("Menunggu hasil pencarian dimuat...")
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

        # print("Mengambil data dari tabel...")
        all_rows = tbody.find_elements(By.TAG_NAME, "tr")[1:]

        data = []
        for row in all_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cells[1].text, cells[3].text]
            data.append(row_data)

        df = pd.DataFrame(data, columns=["Harga_Jual", "Tanggal"])
        df = df[["Tanggal", "Harga_Jual"]]

        df["Tanggal"] = df["Tanggal"].replace(
            {
                "Januari": "January",
                "Februari": "February",
                "Maret": "March",
                "April": "April",
                "Mei": "May",
                "Juni": "June",
                "Juli": "July",
                "Agustus": "August",
                "September": "September",
                "Oktober": "October",
                "November": "November",
                "Desember": "December",
            },
            regex=True,
        )

        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df["Harga_Jual"] = (
            df["Harga_Jual"]
            .str.replace(".", "")
            .str.replace(",", "")
            .apply(lambda x: int(str(x)[:-2]))
        )
        df["Harga_Jual"] = df["Harga_Jual"].astype(float)

        # print("Data yang diambil:")
        # print(df)

        df.to_csv(file_name, index=False, sep=";", quotechar='"', quoting=csv.QUOTE_ALL)
        # print(f"Data saved to {file_name}")
        # print("=====================================")

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()


# Fungsi untuk mendapatkan data suku bunga
def Get_Suku_Bunga(start_date, end_date_fix, file_name):
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        # print("Membuka URL untuk suku bunga...")
        driver.get("https://www.bi.go.id/id/statistik/indikator/BI-Rate.aspx")

        wait = WebDriverWait(driver, 5)

        # print("Mengatur tanggal mulai dan akhir...")
        start_date_input = wait.until(
            EC.presence_of_element_located((By.ID, "TextBoxDateStart"))
        )
        driver.execute_script(
            "arguments[0].value = arguments[1]",
            start_date_input,
            start_date.strftime("%d/%m/%Y"),
        )

        end_date_input = wait.until(
            EC.presence_of_element_located((By.ID, "TextBoxDateEnd"))
        )
        driver.execute_script(
            "arguments[0].value = arguments[1]",
            end_date_input,
            end_date_fix.strftime("%d/%m/%Y"),
        )

        # print("Mengklik tombol pencarian...")
        search_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_ctl54_g_78f62327_0ad4_4bb8_b958_a315eccecc27_ctl00_ButtonSearch",
                )
            )
        )
        search_button.click()

        # print("Menunggu hasil pencarian dimuat...")
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

        # print("Mengambil data dari tabel...")
        all_rows = tbody.find_elements(By.TAG_NAME, "tr")

        data = []
        for row in all_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells[:2]]
            data.append(row_data)

        df = pd.DataFrame(data, columns=["Tanggal", "Suku_Bunga"])
        df = df[["Tanggal", "Suku_Bunga"]]

        df["Tanggal"] = df["Tanggal"].replace(
            {
                "Januari": "January",
                "Februari": "February",
                "Maret": "March",
                "April": "April",
                "Mei": "May",
                "Juni": "June",
                "Juli": "July",
                "Agustus": "August",
                "September": "September",
                "Oktober": "October",
                "November": "November",
                "Desember": "December",
            },
            regex=True,
        )

        df["Tanggal"] = pd.to_datetime(df["Tanggal"]).dt.strftime("%B %Y")
        df["Suku_Bunga"] = df["Suku_Bunga"].str.replace("%", "").astype(float)

        # print("Data yang diambil:")
        # print(df)

        df.to_csv(file_name, index=False, sep=";", quotechar='"', quoting=csv.QUOTE_ALL)
        # print(f"Data saved to {file_name}")
        # print("=====================================")

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()


# Fungsi untuk mendapatkan data dari tabel TradingEconomics
def Get_TheFed(file_name):
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get("https://id.tradingeconomics.com/united-states/interest-rate")
        height = driver.execute_script("return document.body.scrollHeight")
        middle_position = height / 3
        driver.execute_script(f"window.scrollTo(0, {middle_position});")

        # print("Scrolled to the middle of the page. Wait for 2 seconds...")
        # time.sleep(2)

        tbody = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tbody"))
        )[1]

        fifth_row = tbody.find_elements(By.TAG_NAME, "tr")[4]
        cell = fifth_row.find_elements(By.TAG_NAME, "td")[1]
        cell_text = cell.text

        df = pd.DataFrame([[cell_text]], columns=["TheFed"])
        current_date = datetime.now().strftime("%B %Y")
        df.insert(0, "Tanggal", current_date)

        # print(df)

        df.to_csv(file_name, index=False, sep=";", quotechar='"', quoting=csv.QUOTE_ALL)
        # print(f"Data saved to {file_name}")
        # print("=====================================")

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()


# Fungsi untuk mendapatkan data dari tabel
def Get_Inflasi(start_date_inflasi, end_date_fix, file_name):
    # Mulai browser (Chrome)
    driver = webdriver.Chrome()
    # Maksimalkan jendela browser
    driver.maximize_window()

    try:
        # Buka URL
        driver.get("https://www.bi.go.id/id/statistik/indikator/data-inflasi.aspx")
        start_date_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "TextBoxDateFrom"))
        )
        driver.execute_script(
            "arguments[0].value = arguments[1]",
            start_date_input,
            start_date_inflasi.strftime("%m/%Y"),
        )
        # print("Start date set successfully using JavaScript")

        # Set the end date using JavaScript
        end_date_input = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "TextBoxDateTo"))
        )
        driver.execute_script(
            "arguments[0].value = arguments[1]",
            end_date_input,
            end_date_fix.strftime("%m/%Y"),
        )
        # print("End date set successfully using JavaScript")

        # Tunggu sebentar untuk memastikan elemen lain dimuat
        # time.sleep(2)

        search_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_ctl54_g_1f0a867d_90e9_4a92_b1c8_de34738fc4f1_ctl00_ButtonCari",
                )
            )
        )
        search_button.click()
        # print("Search button clicked")

        # Tunggu agar halaman sepenuhnya dimuat
        # time.sleep(2)

        # Extract value from the table
        tbody = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        # Find all rows
        all_rows = tbody.find_elements(By.TAG_NAME, "tr")

        # Extract data rows starting from the second row
        data = []
        for row in all_rows[0:1]:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [
                cells[0].text,
                cells[1].text,
            ]  # Get only the first two <td> elements
            data.append(row_data)

        # Create DataFrame
        df = pd.DataFrame(data, columns=["Tanggal", "Inflasi"])

        # Translate bulan tanggal ke inggris
        df["Tanggal"] = df["Tanggal"].str.replace("Januari", "January")
        df["Tanggal"] = df["Tanggal"].str.replace("Februari", "February")
        df["Tanggal"] = df["Tanggal"].str.replace("Maret", "March")
        df["Tanggal"] = df["Tanggal"].str.replace("April", "April")
        df["Tanggal"] = df["Tanggal"].str.replace("Mei", "May")
        df["Tanggal"] = df["Tanggal"].str.replace("Juni", "June")
        df["Tanggal"] = df["Tanggal"].str.replace("Juli", "July")
        df["Tanggal"] = df["Tanggal"].str.replace("Agustus", "August")
        df["Tanggal"] = df["Tanggal"].str.replace("September", "September")
        df["Tanggal"] = df["Tanggal"].str.replace("Oktober", "October")
        df["Tanggal"] = df["Tanggal"].str.replace("November", "November")
        df["Tanggal"] = df["Tanggal"].str.replace("Desember", "December")

        # Extract month and year only
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        df["Tanggal"] = df["Tanggal"].dt.strftime("%B %Y")

        # Convert Inflasi to float after removing %
        df["Inflasi"] = df["Inflasi"].str.replace("%", "")
        df["Inflasi"] = df["Inflasi"].astype(float)

        # print("Data yang diambil:")
        # print(df)

        # Save dataframe to CSV
        df.to_csv(
            file_name,
            index=False,
            sep=";",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
        )

        # print(f"Data saved to {file_name}")
        # print("=====================================")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the browser when finished
        driver.quit()


# Menghitung tanggal dua minggu yang lalu dari hari ini
date_now = datetime.now().date()
end_date_fix = date_now - timedelta(days=1)
start_date = date_now - timedelta(days=30)

# Menghitung tanggal dua bulan yang lalu dari hari ini
start_date_bunga = date_now - timedelta(days=60)

# Menghitung Tanggal untuk Inflasi
start_date_inflasi = date_now - timedelta(days=60)

# Menjalankan fungsi secara paralel
with ThreadPoolExecutor(max_workers=4) as executor:
    executor.submit(
        Get_USD,
        "Time Series",
        "USD",
        start_date,
        end_date_fix,
        "Selenium/Data_Raw/USD_RAW.csv",
    )
    executor.submit(
        Get_Suku_Bunga,
        start_date_bunga,
        end_date_fix,
        "Selenium/Data_Raw/Suku_Bunga_RAW.csv",
    )
    executor.submit(
        Get_TheFed,
        "Selenium/Data_Raw/TheFed_RAW.csv",
    )
    executor.submit(
        Get_Inflasi,
        start_date_inflasi,
        end_date_fix,
        "Selenium/Data_Raw/Inflasi_RAW.csv",
    )
import pandas as pd

# Baca data USD
df_usd = pd.read_csv("Selenium/Data_Raw/USD_RAW.csv", sep=";", parse_dates=["Tanggal"])
print("Data USD:")
print(df_usd)

# Baca data suku bunga
df_suku_bunga = pd.read_csv(
    "Selenium/Data_Raw/Suku_Bunga_RAW.csv", sep=";", parse_dates=["Tanggal"]
)
print("\nData Suku Bunga:")
print(df_suku_bunga)

# Baca data Inflasi
df_inflasi = pd.read_csv(
    "Selenium/Data_Raw/Inflasi_RAW.csv", sep=";", parse_dates=["Tanggal"]
)
print("\nData Inflasi:")
print(df_inflasi)

df_thefed = pd.read_csv(
    "Selenium/Data_Raw/TheFed_RAW.csv", sep=";", parse_dates=["Tanggal"]
)
print("\nData The Fed:")
print(df_thefed)

# Gabungkan DataFrame USD dengan DataFrame Suku Bunga berdasarkan bulan
df_merged = pd.merge(df_usd, df_suku_bunga, on="Tanggal", how="left")

# Pastikan data tanggal terurut secara ascending
df_merged.sort_values(by="Tanggal", inplace=True)

# Isi nilai NaN pada kolom Suku Bunga dengan nilai yang sesuai berdasarkan bulan
bulan_usd = df_usd["Tanggal"].dt.strftime("%B %Y").unique()

sukubunga_sebelumnya = df_thefed["TheFed"].iloc[0]

for bulan in bulan_usd:
    # Mencari nilai inflasi untuk bulan tersebut
    sukubunga_bulan = df_suku_bunga.loc[
        df_suku_bunga["Tanggal"].dt.strftime("%B %Y") == bulan, "Suku_Bunga"
    ]

    # Jika ada nilai inflasi, gunakan itu sebagai inflasi sebelumnya
    if not sukubunga_bulan.empty:
        sukubunga_sebelumnya = sukubunga_bulan.values[0]

    # Mengisi nilai inflasi pada df_merged
    df_merged.loc[df_merged["Tanggal"].dt.strftime("%B %Y") == bulan, "Suku_Bunga"] = (
        sukubunga_sebelumnya
    )

# Merge DataFrame dengan DataFrame TheFed berdasarkan bulan
df_merged = pd.merge(df_merged, df_thefed, on="Tanggal", how="left")

thefed_sebelumnya = df_thefed["TheFed"].iloc[0]

for bulan in bulan_usd:
    # Mencari nilai inflasi untuk bulan tersebut
    thefed_bulan = df_thefed.loc[
        df_thefed["Tanggal"].dt.strftime("%B %Y") == bulan, "TheFed"
    ]

    # Jika ada nilai inflasi, gunakan itu sebagai inflasi sebelumnya
    if not thefed_bulan.empty:
        thefed_sebelumnya = thefed_bulan.values[0]

    # Mengisi nilai inflasi pada df_merged
    df_merged.loc[df_merged["Tanggal"].dt.strftime("%B %Y") == bulan, "TheFed"] = (
        thefed_sebelumnya
    )

# Merge DataFrame dengan DataFrame Inflasi berdasarkan bulan
df_merged = pd.merge(df_merged, df_inflasi, on="Tanggal", how="left")

# Menginisialisasi variabel untuk menyimpan nilai inflasi sebelumnya
inflasi_sebelumnya = df_inflasi["Inflasi"].iloc[0]

# Iterasi setiap bulan dalam bulan_usd
for bulan in bulan_usd:
    # Mencari nilai inflasi untuk bulan tersebut
    inflasi_bulan = df_inflasi.loc[
        df_inflasi["Tanggal"].dt.strftime("%B %Y") == bulan, "Inflasi"
    ]

    # Jika ada nilai inflasi, gunakan itu sebagai inflasi sebelumnya
    if not inflasi_bulan.empty:
        inflasi_sebelumnya = inflasi_bulan.values[0]

    # Mengisi nilai inflasi pada df_merged
    df_merged.loc[df_merged["Tanggal"].dt.strftime("%B %Y") == bulan, "Inflasi"] = (
        inflasi_sebelumnya
    )

# Tampilkan DataFrame gabungan
print("\nDataFrame Gabungan:")
print(df_merged)

# Simpan DataFrame gabungan ke file CSV
import csv

df_merged.to_csv(
    "Selenium/Data_Raw/Merged_Data.csv",
    index=False,
    sep=";",
    quotechar='"',
    quoting=csv.QUOTE_ALL,
)


# Path: Selenium/PenyatuanDataFrame.py
def format_cleaning(value):
    value_str = str(value)
    if len(value_str) > 5:
        return value_str[:5]
    elif len(value_str) < 5:
        return value_str.ljust(5, "0")
    else:
        return value_str


# Membaca df
df = pd.read_csv(
    "C:/Users/kybpp/OneDrive/Desktop/jupyter/Selenium/Data_Raw/Merged_Data.csv",
    delimiter=";",
)
df = df.replace(",", ".", regex=True)

df["Harga_Jual"] = df["Harga_Jual"].apply(format_cleaning)

df["Harga_Jual"] = df["Harga_Jual"].astype(float)
df["Suku_Bunga"] = df["Suku_Bunga"].astype(float)
df["TheFed"] = df["TheFed"].astype(float)
df["Inflasi"] = df["Inflasi"].astype(float)
# df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d/%m/%Y")
df = df[::-1].reset_index(drop=True)
df.reset_index(drop=True, inplace=True)

import pandas as pd
import csv

# Baca kedua file CSV
update_data = pd.read_csv(
    "C:/Users/kybpp/OneDrive/Desktop/jupyter/Selenium/Data_Raw/Merged_Data.csv",
    delimiter=";",
)
prophet_data = pd.read_csv(
    "C:/Users/kybpp/OneDrive/Desktop/jupyter/Data_USD/data_prophet.csv", delimiter=","
)

# Gabungkan kedua DataFrame
updated_data = pd.concat([prophet_data, update_data], ignore_index=True)
updated_data = updated_data.drop_duplicates(subset=["Tanggal"], keep="first")
updated_data = updated_data.sort_values(by="Tanggal", ascending=True)
updated_data = updated_data.reset_index(drop=True)
updated_data = updated_data[
    ["Tanggal", "Harga_Jual", "Suku_Bunga", "TheFed", "Inflasi"]
]

# Simpan hasil gabungan ke dalam file CSV baru
updated_data.to_csv("Data_USD/data_prophet.csv", index=False, quoting=csv.QUOTE_ALL)

print("Data lama dan baru berhasil digabung dan disimpan ke Folder Data_USD")
print("=========================================================================")
print(updated_data)
