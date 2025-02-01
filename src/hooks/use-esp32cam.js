import { useState } from "react";

export function useEsp32Cam() {
  const [stream, setStream] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const start = async () => {
    const esp32StreamUrl = "http://192.168.137.67:81/stream";
    setStream(esp32StreamUrl);
    setIsStreaming(true);
    return esp32StreamUrl;
  };

  const stop = () => {
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
