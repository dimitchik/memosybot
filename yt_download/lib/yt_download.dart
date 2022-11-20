import 'dart:io';

import 'package:youtube_explode_dart/youtube_explode_dart.dart';

Future<String?> download(String id) async {
  final yt = YoutubeExplode();
  final manifest = await yt.videos.streamsClient.getManifest(id);
  var streamInfo = manifest.muxed.bestQuality;
  final stream = yt.videos.streamsClient.get(streamInfo);
  final filePath = '$id.mp4';
  var file = File(filePath);
  var fileStream = file.openWrite();
  await stream.pipe(fileStream);
  await fileStream.flush();
  await fileStream.close();
  return filePath;
}
