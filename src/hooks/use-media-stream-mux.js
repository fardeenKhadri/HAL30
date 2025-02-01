export function useMediaStream(type) {
  if (!["webcam", "screen"].includes(type)) {
    throw new Error('Invalid type. Expected "webcam" or "screen".');
  }

  let stream = null;
  let isStreaming = false;

  const start = async () => {
    if (type === "webcam") {
      stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
    } else if (type === "screen") {
      stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: false,
      });
    }
    isStreaming = true;
    return stream;
  };

  const stop = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    isStreaming = false;
  };

  return {
    type,
    start,
    stop,
    get isStreaming() {
      return isStreaming;
    },
    get stream() {
      return stream;
    },
  };
}
