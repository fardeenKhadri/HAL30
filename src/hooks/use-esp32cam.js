import { useState } from "react";
import { createMediaStreamFromImage } from "../lib/utils"; // Import utility

export function useEsp32Cam() {
  const [stream, setStream] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const start = async () => {
    const esp32StreamUrl = "http://192.168.137.137:81/stream";
    const mediaStream = await createMediaStreamFromImage(esp32StreamUrl);
    setStream(mediaStream);
    setIsStreaming(true);
    return mediaStream;
  };

  const stop = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
    setStream(null);
    setIsStreaming(false);
  };

  return {
    type: "esp32cam",
    start,
    stop,
    isStreaming,
    stream,
  };
}
