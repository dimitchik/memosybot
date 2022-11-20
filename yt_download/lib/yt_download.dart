import 'dart:io';

import 'package:youtube_explode_dart/youtube_explode_dart.dart';

Future<String?> download(String id) async {
  final yt = YoutubeExplode();
  final manifest = await yt.videos.streamsClient.getManifest(id);
  MuxedStreamInfo streamInfo;
  if (manifest.muxed.sortByVideoQuality().length > 1) {
    streamInfo = manifest.muxed.sortByVideoQuality()[1];
  } else {
    streamInfo = manifest.muxed.sortByVideoQuality().first;
  }
  final stream = yt.videos.streamsClient.get(streamInfo);
  final filePath = '$id.mp4';
  final file = File(filePath);
  final fileStream = file.openWrite();
  await stream.pipe(fileStream);
  await fileStream.flush();
  await fileStream.close();
  return filePath;
}
