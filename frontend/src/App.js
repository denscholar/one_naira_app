import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import HomePage from './home/HomePage'
import Login from './Login';
import Register from './register/Register';
import PhoneLogin from './phoneRegister/PhoneLogin';
import RegerateOTP from './regenerateOTP/RegerateOTP';


function App() {
  return (
    <div className="App">
      <ToastContainer></ToastContainer>
      <BrowserRouter>
      <Routes>
        <Route path='/' element={<HomePage/>}>Home</Route>
        <Route path='/login' element={<Login/>}>Login</Route>
        <Route path='/phone_login' element={<PhoneLogin/>}>Phone Login</Route>
        <Route path='/regenerate_otp' element={<RegerateOTP/>}>Regenerate OTP</Route>
        <Route path='/register' element={<Register/>}>Register</Route>
      </Routes>
      </BrowserRouter>

    </div>
  );
}

export default App;
