import React, { useRef, useState } from "react";
import { API_KEY, uri } from "../../constants";
import { LiveAPIProvider } from "../../contexts/LiveAPIContext";
import ControlTray from "../../components/shared/ControlTray";

const Home = () => {
  const videoRef = useRef(null);

  const [videoStream, setVideoStream] = useState(null);

  if (!API_KEY) {
    throw new Error(
      "API key is required to use the StreamingConsole component."
    );
  }
  return (
    <section className="flex flex-1">
      <LiveAPIProvider url={uri} apiKey={API_KEY}>
        <video
          className={"border max-h-fit max-w-[90%] "}
          ref={videoRef}
          autoPlay
          playsInline
        />
        <ControlTray videoRef={videoRef} onVideoStreamChange={setVideoStream} />
      </LiveAPIProvider>
    </section>
  );
};

export default Home;
