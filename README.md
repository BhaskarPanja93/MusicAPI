# 🎶 **MusicAPI** - Your Gateway to All Things Music! 🎧

Welcome to **MusicAPI** – a **free, fast, and easy-to-use API** that lets you fetch detailed song data, including song names, YouTube & Spotify URLs, audio files, thumbnails, and more! It's like having your very own personal music assistant, all wrapped up in a neat API package. 🚀

### **Features:**
- 🎵 **Get Song Data**: Fetch all essential details like song name, thumbnail, duration, and more.
- 🔗 **YouTube & Spotify Integration**: Direct links to song videos on YouTube and audio streaming on Spotify.
- 📦 **Audio Streaming/Download**: Stream or download the song audio directly via a clean audio URL.
- ⚡ **Fast & Cached**: Once fetched, song data is cached to ensure faster subsequent requests, without relying on third-party APIs each time.
- 🌐 **Web Interface**: No coding required – use the built-in web interface to search and play songs with a few clicks. 🎶

### **How it Works:**
1. **Request a Song**: Send a request with a song ID to the API. 
2. **Data Fetching**: The backend fetches all song details (YouTube, Spotify, etc.) in real-time and stores them.
3. **Return the Data**: The API responds with the song’s data, including URLs, audio file links, and more.
4. **Caching**: The data is cached to prevent unnecessary API calls to YouTube and Spotify, making the system super efficient.

### **🎵 API Endpoints**

**1. Request Song ID**
- **Endpoint**: `https://bhindi1.ddns.net/music/api/prepare/{song_name}`
- **Method**: GET
- **Description**: Provide the song name, and the API returns a song ID.

**2. Request Song Data by ID**
- **Endpoint**: `https://bhindi1.ddns.net/music/api/fetch/{song_id}`
- **Method**: GET
- **Description**: Using the song ID, fetch detailed song information including URLs for YouTube, Spotify, and the audio file.

---

### **🌐 Web Interface**

Want to try out the API without writing code? No problem! Just head to the bundled web interface and start playing songs in seconds.

👉 **Visit the Web Interface**: [MusicAPI Web Interface](https://bhindi1.ddns.net/bpd/music)

---

### **⚙️ Technologies Used**

- **Backend**: Python
- **Database**: MySQL (for caching song data)
- **External APIs**: YouTube Data API, Spotify Web API
- **Frontend**: HTML, CSS, JavaScript (for the web interface)

---

### **💡 Why Use MusicAPI?**

- **Speed**: Enjoy fast responses due to intelligent caching of song data.
- **Convenience**: Fetch everything you need with just one request. No more manual searching on YouTube or Spotify.
- **Free to Use**: As an open-source project, **MusicAPI** is free. 🎉
- **Fully Integrated**: Get all your music info (audio, video, metadata) in a single place.

---

### **⚡ Support**

For any issues or support, feel free to open an issue in the GitHub repository. 

---

With MusicAPI, music just got a whole lot easier to access. Enjoy listening, streaming, and sharing! 🎶✨
