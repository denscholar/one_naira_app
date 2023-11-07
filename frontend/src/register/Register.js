import { useState } from "react";
import { toast } from "react-toastify";

const Register = () => {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email_address: "",
    // phone_number: '',
    password1: "",
    password2: "",
  });

  const handleSubmit = (event) => {
    event.preventDefault();
    let hasError = false;

    fetch("https://onenairapay.com/auth/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // include cookies in the request
      body: JSON.stringify(formData),
    })
    .then((response) => {
      if (!response.ok) {
        hasError = true;
        if (response.status === 400) {
          console.log(response.status);
          toast.error("Your session has expired");
        } else {
          throw new Error("Network response was not ok");
        }
      }
      return response.json();
    })
    .then((data) => {
      if (!hasError) {
        console.log(data);
        toast.success("Registered successfully");
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
    <div className="offset-lg-3 col-lg-6">
      <form className="container" onSubmit={handleSubmit}>
        <div className="card">
          <div className="card-header">
            <h1>User Registeration</h1>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-lg-6">
                <div className="form-group">
                  <label htmlFor="first_name">
                    First Name<span className="errmsg">*</span>
                  </label>
                  <input
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="form-control"
                    type="text"
                  />
                </div>
              </div>
              <div className="col-lg-6">
                <div className="form-group">
                  <label htmlFor="last_name">
                    Last Name<span className="errmsg">*</span>
                  </label>
                  <input
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="form-control"
                    type="text"
                  />
                </div>
              </div>
              <div className="col-lg-6">
                <div className="form-group">
                  <label htmlFor="email">
                    Email <small className="errmsg">optional</small>
                  </label>
                  <input
                    id="email"
                    name="email_address"
                    value={formData.email_address}
                    onChange={handleChange}
                    className="form-control"
                    type="email"
                  />
                </div>
              </div>
              {/* <div className='col-lg-6'>
                    <div className='form-group'>
                        <label htmlFor="">Phone Number<span className='errmsg'>*</span></label>
                        <input name='phone_number' value={formData.phone_number} onChange={handleChange} className='form-control' type="text"/>
                    </div>
                </div>                */}
              <div className="col-lg-6">
                <div className="form-group">
                  <label htmlFor="password">
                    Password<span className="errmsg">*</span>
                  </label>
                  <input
                    id="password"
                    name="password1"
                    value={formData.password1}
                    onChange={handleChange}
                    className="form-control"
                    type="password"
                  />
                </div>
              </div>
              <div className="col-lg-6">
                <div className="form-group">
                  <label htmlFor="confirm_password">
                    Confirm Password<span className="errmsg">*</span>
                  </label>
                  <input
                    id="confirm_password"
                    name="password2"
                    value={formData.password2}
                    onChange={handleChange}
                    className="form-control"
                    type="password"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="card-footer">
            <button type="submit" className="btn btn-primary">
              Registeer
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Register;
