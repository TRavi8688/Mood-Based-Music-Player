<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Moodify - Upload Mood</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-black text-white font-sans">

  <div class="min-h-screen flex flex-col items-center justify-center">
    <h1 class="text-green-500 text-4xl font-bold mb-4">🎵 Moodify</h1>
    <p class="text-white mb-6">Upload your image to detect your mood</p>

    <form action="/predict" method="POST" enctype="multipart/form-data" class="bg-gray-900 p-6 rounded-lg shadow-lg">
      <input type="file" name="image" accept="image/*" class="mb-4 block w-full text-white" required />
      <button type="submit" class="bg-green-500 text-black px-4 py-2 rounded hover:bg-green-400">
        Detect Mood
      </button>
    </form>
  </div>

</body>
</html>
