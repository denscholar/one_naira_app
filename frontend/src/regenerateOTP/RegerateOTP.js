import { useState } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import "./regenerate.css";

const RegenerateOTP = () => {
  const navigate = useNavigate();

  // function to get the CSRF token from the cookie
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    console.log(value);
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop().split(";").shift();
    }
  }

  const handleRegenerateOTP = (event) => {
    event.preventDefault();

    // const sessionId = sessionStorage.getItem("sessionid");
    const sessionid = localStorage.getItem("sessionid");
    console.log(sessionid);

    fetch(`https://onenairapay.com/auth/register/regenerate_otp/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "Authorization": `Token ${sessionid}`
      },
      credentials: "include",
      body: JSON.stringify({}),
    })
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        toast.success("OTP regenerated successfully");
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        toast.error("Failed to regenerate OTP: " + error.message);
      });
  };

  // otp verification
  const [otpData, setOtp] = useState({
    otp: "",
  });

  const handleSubmitOTP = (event) => {
    event.preventDefault();
    fetch("https://onenairapay.com/auth/register/verify_otp/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(otpData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log(data);
        toast.success("Verification successful");
        navigate("/register");
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        toast.error("Failed: " + error.message);
      });
  };

  const handleOTPChange = (e) => {
    setOtp({
      ...otpData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="">
      <div className="container_wrapper">
        <form className="otp_input" onSubmit={handleSubmitOTP}>
          <h4>Type your OTP here</h4>
          <div className="input_button">
            <input
              id="otp"
              name="otp"
              value={otpData.otp}
              onChange={handleOTPChange}
              className="form-control"
              type="number"
            />
            <button type="submit" className="btn btn-primary">
              Submit
            </button>
          </div>
        </form>
      </div>
      <div className="regenerate_button">
        <form onSubmit={handleRegenerateOTP}>
          <div className="card-footer">
            <button type="resend_otp" className="btn btn-primary">
              Resend OTP
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegenerateOTP;
