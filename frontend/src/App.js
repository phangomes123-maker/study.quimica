import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import Nav from "./components/Nav";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Topics from "./pages/Topics";
import TopicDetail from "./pages/TopicDetail";
import Revision from "./pages/Revision";
import Progress from "./pages/Progress";
import Scanner from "./pages/Scanner";
import TutorChat from "./components/TutorChat";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Nav />
        <main className="min-h-screen">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/topicos" element={<Topics />} />
            <Route path="/topico/:id" element={<TopicDetail />} />
            <Route path="/revisao" element={<Revision />} />
            <Route path="/progresso" element={<Progress />} />
            <Route path="/scanner" element={<Scanner />} />
          </Routes>
        </main>
        <Footer />
        <TutorChat />
        <Toaster position="top-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;
