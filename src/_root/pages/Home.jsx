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
    <section className="flex w-full h-screen p-5">
      <LiveAPIProvider url={uri} apiKey={API_KEY}>
        <div className="flex w-full flex-col items-center gap-5">
          <video
            className={"border w-fit "}
            ref={videoRef}
            autoPlay
            playsInline
          />
          <ControlTray
            videoRef={videoRef}
            onVideoStreamChange={setVideoStream}
          />
        </div>
      </LiveAPIProvider>
    </section>
  );
};

export default Home;
