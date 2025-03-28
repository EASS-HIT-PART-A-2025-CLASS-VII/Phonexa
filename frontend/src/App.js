import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import StartPage from './Components/StartPage';
import Game from './Components/Game';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StartPage/>} />
        <Route path="/game" element={<Game/>} />
      </Routes>
    </BrowserRouter>  
  );
}

export default App;

