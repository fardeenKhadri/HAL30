import React, { useRef, useState } from "react";
import { API_KEY } from "../../constants";

const Home = () => {
  const videoRef = useRef(null);

  const [videoStream, setVideoStream] = useState(null);

  if (!API_KEY) {
    throw new Error(
      "API key is required to use the StreamingConsole component."
    );
  }
  return <div>Home</div>;
};

export default Home;
