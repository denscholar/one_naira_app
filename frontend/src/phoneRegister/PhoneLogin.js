import { useState } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import "./phoneLogin.css";

const PhoneLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ phone_number: "" });

  const handleSubmit = (event) => {
    let hasError = false;
    event.preventDefault();
    fetch("https://onenairapay.com/auth/register/phone/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // include cookies in the request
      body: JSON.stringify(formData),
    })
      .then((response) => {
        console.log(response.status);
        if (!response.ok) {
          hasError = true;
          if (response.status === 405) {
            toast.error("Phone number already already exist. Please login");
            navigate("/register");
          } else if (response.status === 400) {
            toast.error("Phone number verified. Please register");
            navigate("/register");
          } else {
            throw new Error("Network response was not ok");
          }
        }
        const sessionid = response.headers.get("X-Session-Id");
        sessionStorage.setItem("sessionid", sessionid);
        return response.json();
      })
      .then((data) => {
        if (!hasError) {
          localStorage.setItem("sessionid", data.sessionid);
          toast.success("OTP sent to your phone successfully");
          navigate("/regenerate_otp");
        }
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        toast.error("Failed: " + error.message);
      });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };
  return (
    <div className="input_name_login">
      <form onSubmit={handleSubmit}>
        <label htmlFor="Phone_number">
          Phone Number<span className="errmsg">*</span>
        </label>
        <input
          id="phone_number"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleChange}
          className="form-control"
          type="text"
        />

        <div className="card-footer">
          <button type="submit" className="btn btn-primary">
            submit
          </button>
        </div>
      </form>
    </div>
  );
};

export default PhoneLogin;
