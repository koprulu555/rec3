<?php
// Config dosyasını oku
$config = json_decode(file_get_contents(__DIR__ . '/final-config.json'), true);

if (!$config) {
    die("Config yüklenemedi!\n");
}

$mainUrl = $config['mainUrl'];
$swKey = $config['swKey'];
$userAgent = $config['userAgent'];
$referer = $config['referer'];
$m3uUserAgent = 'googleusercontent';

echo "🎬 M3U Oluşturucu Başlıyor...\n";
echo "🔗 API: $mainUrl\n";

// Context ayarları
$context = stream_context_create([
    'http' => [
        'method' => 'GET',
        'header' => "User-Agent: $userAgent\r\nReferer: $referer\r\n",
        'timeout' => 20,
        'ignore_errors' => true
    ],
    'ssl' => [
        'verify_peer' => false,
        'verify_peer_name' => false
    ]
]);

$m3uContent = "#EXTM3U\n";

// 📺 CANLI YAYINLAR
echo "📺 Canlı yayınlar alınıyor...\n";
$totalChannels = 0;

for ($page = 0; $page < 4; $page++) {
    $apiUrl = "$mainUrl/api/channel/by/filtres/0/0/$page/$swKey";
    $response = @file_get_contents($apiUrl, false, $context);
    
    if ($response) {
        $data = json_decode($response, true);
        if (is_array($data)) {
            foreach ($data as $content) {
                if (isset($content['sources'])) {
                    foreach ($content['sources'] as $source) {
                        if (($source['type'] ?? '') === 'm3u8' && !empty($source['url'])) {
                            $totalChannels++;
                            $title = $content['title'] ?? 'Başlıksız';
                            $image = $content['image'] ?? '';
                            $categories = isset($content['categories']) ? implode(", ", array_column($content['categories'], 'title')) : 'Genel';
                            
                            $m3uContent .= "#EXTINF:-1 tvg-id=\"{$content['id']}\" tvg-name=\"$title\" tvg-logo=\"$image\" group-title=\"$categories\", $title\n";
                            $m3uContent .= "#EXTVLCOPT:http-user-agent=$m3uUserAgent\n";
                            $m3uContent .= "#EXTVLCOPT:http-referrer=$referer\n";
                            $m3uContent .= "{$source['url']}\n";
                        }
                    }
                }
            }
        }
    }
}
echo "✅ Canlı: $totalChannels kanal\n";

// 🎬 FİLMLER
echo "🎬 Filmler alınıyor...\n";
$movieCategories = [
    "0" => "Son Filmler", "14" => "Aile", "1" => "Aksiyon", "13" => "Animasyon",
    "19" => "Belgesel", "4" => "Bilim Kurgu", "2" => "Dram", "10" => "Fantastik",
    "3" => "Komedi", "8" => "Korku", "17" => "Macera", "5" => "Romantik"
];

$totalMovies = 0;
foreach ($movieCategories as $categoryId => $categoryName) {
    for ($page = 0; $page < 3; $page++) {
        $apiUrl = "$mainUrl/api/movie/by/filtres/$categoryId/created/$page/$swKey";
        $response = @file_get_contents($apiUrl, false, $context);
        
        if ($response) {
            $data = json_decode($response, true);
            if (is_array($data)) {
                foreach ($data as $content) {
                    if (isset($content['sources'])) {
                        foreach ($content['sources'] as $source) {
                            if (($source['type'] ?? '') === 'm3u8' && !empty($source['url'])) {
                                $totalMovies++;
                                $title = $content['title'] ?? 'Başlıksız Film';
                                $image = $content['image'] ?? '';
                                
                                $m3uContent .= "#EXTINF:-1 tvg-id=\"{$content['id']}\" tvg-name=\"$title\" tvg-logo=\"$image\" group-title=\"Film-$categoryName\", $title\n";
                                $m3uContent .= "#EXTVLCOPT:http-user-agent=$m3uUserAgent\n";
                                $m3uContent .= "#EXTVLCOPT:http-referrer=$referer\n";
                                $m3uContent .= "{$source['url']}\n";
                            }
                        }
                    }
                }
            }
        }
    }
}
echo "✅ Filmler: $totalMovies film\n";

// 📺 DİZİLER
echo "📺 Diziler alınıyor...\n";
$totalSeries = 0;
for ($page = 0; $page < 3; $page++) {
    $apiUrl = "$mainUrl/api/serie/by/filtres/0/created/$page/$swKey";
    $response = @file_get_contents($apiUrl, false, $context);
    
    if ($response) {
        $data = json_decode($response, true);
        if (is_array($data)) {
            foreach ($data as $content) {
                if (isset($content['sources'])) {
                    foreach ($content['sources'] as $source) {
                        if (($source['type'] ?? '') === 'm3u8' && !empty($source['url'])) {
                            $totalSeries++;
                            $title = $content['title'] ?? 'Başlıksız Dizi';
                            $image = $content['image'] ?? '';
                            
                            $m3uContent .= "#EXTINF:-1 tvg-id=\"{$content['id']}\" tvg-name=\"$title\" tvg-logo=\"$image\" group-title=\"Diziler\", $title\n";
                            $m3uContent .= "#EXTVLCOPT:http-user-agent=$m3uUserAgent\n";
                            $m3uContent .= "#EXTVLCOPT:http-referrer=$referer\n";
                            $m3uContent .= "{$source['url']}\n";
                        }
                    }
                }
            }
        }
    }
}
echo "✅ Diziler: $totalSeries dizi\n";

// 💾 Dosyaya yaz
$outputDir = __DIR__ . '/../m3u-output';
if (!is_dir($outputDir)) {
    mkdir($outputDir, 0755, true);
}

$outputFile = "$outputDir/rectv-playlist.m3u";
file_put_contents($outputFile, $m3uContent);

$totalItems = $totalChannels + $totalMovies + $totalSeries;
echo "🎉 İŞLEM TAMAMLANDI!\n";
echo "📊 Toplam: $totalItems içerik\n";
echo "💾 Dosya: $outputFile\n";
echo "📏 Boyut: " . round(filesize($outputFile) / 1024 / 1024, 2) . " MB\n";
?>
