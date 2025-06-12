<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Moodify - Upload Mood</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="icon" href="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" />
</head>
<body class="bg-black text-white font-sans flex items-center justify-center min-h-screen">

  <div class="bg-gray-900 p-8 rounded-xl shadow-xl w-full max-w-md text-center">
    <h1 class="text-green-500 text-4xl font-bold mb-4">🎵 Moodify</h1>
    <p class="text-gray-300 mb-6 text-lg">Upload your image to detect your mood</p>

    <form action="/predict" method="POST" enctype="multipart/form-data" class="flex flex-col space-y-4">
      <input 
        type="file" 
        name="image" 
        accept="image/*" 
        class="text-white bg-black border border-gray-700 p-2 rounded focus:outline-none focus:ring-2 focus:ring-green-500" 
        required
      />
      <button 
        type="submit" 
        class="bg-green-500 text-black py-2 px-4 rounded hover:bg-green-400 transition-all duration-300"
      >
        🎧 Detect Mood
      </button>
    </form>
  </div>

</body>
</html>
