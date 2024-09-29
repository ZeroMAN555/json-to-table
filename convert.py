import json
import argparse
import pyfiglet
import sys
import signal

# Kode warna ANSI
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[32m"  # Untuk status 200 dan URL dengan status 200
    YELLOW = "\033[33m"  # Untuk status 403
    RED = "\033[31m"     # Untuk status 404
    BLUE = "\033[34m"    # Untuk status 500
    MAGENTA = "\033[35m"  # Untuk status 503

# Fungsi untuk membatasi panjang teks
def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length - 3] + '...'  # Memotong teks jika lebih panjang dari batas
    return text

# Fungsi untuk menampilkan judul dan subjudul
def print_title():
    title = pyfiglet.figlet_format("json to table")
    subtitle = "By ZeroMAN555"
    print(title)
    print(subtitle)
    print("=" * 80)  # Garis pemisah

# Fungsi untuk menampilkan pesan terima kasih
def print_thank_you():
    thank_you_message = pyfiglet.figlet_format("Terima kasih!")
    print(thank_you_message)

# Fungsi untuk menentukan warna berdasarkan status
def color_status(status):
    if status == 200:
        return Colors.GREEN
    elif status == 403:
        return Colors.YELLOW
    elif status == 404:
        return Colors.RED
    elif status == 500:
        return Colors.BLUE
    elif status == 503:
        return Colors.MAGENTA
    else:
        return Colors.RESET  # Warna default untuk status lainnya

# Fungsi untuk parsing hasil ffuf
def parse_ffuf_results(file_path, output_file=None, show_full=False):
    # Membuka file JSON dan memuat data
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' tidak ditemukan.")
        return
    
    # Memproses hasil ffuf
    results = data.get('results', [])
    
    if not results:
        print("Tidak ada hasil yang ditemukan.")
        return
    
    # Header untuk output
    header = f"{'No.':<4} {'URL':<80} {'Status':<8} {'Length':<8} {'Words':<8} {'Lines':<8}\n"
    header += "-" * 100 + "\n"
    
    # Memproses hasil menjadi string
    output = header
    for idx, result in enumerate(results, start=1):
        url = result.get('url', '')
        status = result.get('status', '')
        length = result.get('length', '')
        words = result.get('words', '')
        lines = result.get('lines', '')
        
        # Memotong URL jika terlalu panjang
        truncated_url = truncate_text(url, 80)
        
        # Menentukan warna untuk status
        colored_status = color_status(status)
        
        # Menentukan warna untuk URL jika status 200
        colored_url = Colors.GREEN if status == 200 else Colors.RESET
        
        # Format output untuk satu baris hasil
        output += f"{idx:<4} {colored_url}{truncated_url:<80}{colored_status}{status:<8}{Colors.RESET} {length:<8} {words:<8} {lines:<8}\n"
    
    # Menampilkan hasil di console atau menulis ke file output jika diberikan
    if output_file:
        try:
            with open(output_file, 'w') as file:
                file.write(output)
            print(f"Hasil telah disimpan ke '{output_file}'")
        except Exception as e:
            print(f"Gagal menyimpan file: {e}")
    else:
        print(output)

    # Menampilkan URL penuh jika opsi full diaktifkan
    if show_full:
        while True:
            try:
                user_input = input("Masukkan nomor URL yang ingin dilihat secara penuh (atau ketik 'clear' untuk membersihkan input, 'exit' untuk keluar): ")
                if user_input.lower() == 'exit':
                    print_thank_you()
                    break
                elif user_input.lower() == 'clear':
                    # Bersihkan layar (jika di terminal)
                    print("\033c", end="")  # Menggunakan ANSI escape untuk membersihkan layar
                    print_title()  # Tampilkan judul kembali
                    print(output)  # Tampilkan hasil kembali
                    continue
                
                index = int(user_input)
                if 1 <= index <= len(results):
                    # Mendapatkan hasil berdasarkan index
                    selected_result = results[index - 1]
                    full_url = selected_result.get('url', 'URL tidak tersedia')
                    status = selected_result.get('status', 'Status tidak tersedia')
                    length = selected_result.get('length', 'Length tidak tersedia')
                    words = selected_result.get('words', 'Words tidak tersedia')
                    lines = selected_result.get('lines', 'Lines tidak tersedia')

                    # Menampilkan detail lengkap
                    print("\nDetail Hasil:")
                    print(f"URL Penuh: {full_url}")
                    print(f"Status: {status}")
                    print(f"Panjang: {length}")
                    print(f"Kata: {words}")
                    print(f"Baris: {lines}\n")
                else:
                    print("Nomor tidak valid. Silakan coba lagi.")
            except ValueError:
                print("Silakan masukkan nomor yang valid atau 'exit'.")

# Menangani Ctrl+C
def signal_handler(sig, frame):
    print_thank_you()
    sys.exit(0)

if __name__ == "__main__":
    # Menangani sinyal Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Menampilkan judul dan subjudul
    print_title()

    # Menggunakan argparse untuk membaca argumen command line
    parser = argparse.ArgumentParser(description="Parse ffuf results JSON and output to terminal or file.")
    parser.add_argument("json_file", help="Path ke file JSON hasil ffuf.")
    parser.add_argument("-o", "--output", help="Path ke file untuk menyimpan hasil output (opsional).")
    parser.add_argument("--full", action="store_true", help="Tampilkan URL penuh.")

    # Mendapatkan argumen dari command line
    args = parser.parse_args()

    # Memanggil fungsi untuk memproses dan menampilkan hasil
    parse_ffuf_results(args.json_file, args.output, args.full)
