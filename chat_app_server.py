import socket
import threading
import queue

HOST = '0.0.0.0'  # Tüm ağ arabirimlerinden bağlantıları kabul et
PORT = 5555       # Kullanılacak yerel port numarası

clients = {}  # Bağlı istemcilerin adreslerini, soketlerini ve isimlerini saklamak için sözlük

def handle_client(client_socket, client_address):
    print(f"Yeni bağlantı: {client_address}")

    try:
        # İstemciden isim bilgisini al
        client_name = client_socket.recv(1024).decode().strip()
        clients[client_address] = (client_socket, client_name)

        while True:
            # İstemciden gelen verileri al
            data = client_socket.recv(1024)

            if not data:
                break  # Veri alınmadıysa döngüyü sonlandır

            # Gelen mesajı diğer istemcilere iletmek için havuza ekle
            sender_name = clients[client_address][1]
            message = f" {data.decode()}"
            message_queue.put(message)

    except ConnectionResetError:
        print(f"Bağlantı kesildi: {client_address}")
    finally:
        # Bağlantıyı kapat
        client_socket.close()
        del clients[client_address]
        print(f"Bağlantı kapatıldı: {client_address}")

def broadcast_messages():
    while True:
        # Mesaj havuzunda yeni mesaj varsa tüm bağlı istemcilere iletilir
        while not message_queue.empty():
            message = message_queue.get()
            for (addr, (sock, name)) in clients.items():
                try:
                    sock.sendall(message.encode())
                except:
                    # İstemci bağlantısı kapatıldıysa istemciyi havuzdan kaldır
                    del clients[addr]

# Soket oluşturma
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Soketi belirtilen IP adresi ve port numarasına bağlama
    server_socket.bind((HOST, PORT))
    print(f"Sunucu {HOST}:{PORT} üzerinde dinleniyor...")

    # İstemcilerden gelen bağlantıları kabul etmeye başlama
    server_socket.listen()

    # Mesaj kuyruğu oluşturma
    message_queue = queue.Queue()

    # Mesaj gönderme thread'i başlatma
    broadcast_thread = threading.Thread(target=broadcast_messages)
    broadcast_thread.start()

    try:
        while True:
            # Bağlantıyı kabul et ve istemci soketini ve adresini al
            client_socket, client_address = server_socket.accept()

            # Her istemci bağlantısı için ayrı bir iş parçacığı oluştur
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

    except KeyboardInterrupt:
        print("Sunucu kapatılıyor...")

    finally:
        server_socket.close()
