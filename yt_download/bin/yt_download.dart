import 'dart:io';

import 'package:args/args.dart';
import 'package:yt_download/yt_download.dart';

const id = 'id';
const startTime = 'start_time';

void main(List<String> arguments) async {
  exitCode = 0; // presume success
  final parser = ArgParser();
  final argResults = parser.parse(arguments).rest;
  final result = await download(argResults[0]);
  stdout.write(result);
}
