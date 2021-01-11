import Vue from "vue";
import axios from "axios";
import VueAxios from "vue-axios";

const API_URL = `${process.env.VUE_APP_API_BASE_URL}/api/v1`;
const STATIC_URL = `${process.env.VUE_APP_API_BASE_URL}/static`;

let isRefreshing = false;
const Api = {
  init() {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = API_URL;
    Vue.axios.defaults.withCredentials = true;

    axios.interceptors.response.use(
      response => {
        return response;
      },
      async err => {
        if (err.response) {
          const {
            response: { status, data }
          } = err;
          if (status === 401) {
            if (data.message === "Login is required.") {
              window.alert(data.message);
              return Promise.reject(err);
            } else if (data.message === "CSRF token is missing.") {
              // login is asummed
              if (!isRefreshing) {
                isRefreshing = true;
                try {
                  await AuthApi.start_session();
                  const resp = await Vue.axios.request({
                    url: err.config.url,
                    method: err.config.method,
                    params: err.config.params,
                    data: err.config.data,
                    headers: err.config.headers
                  });
                  isRefreshing = false;
                  return new Promise(resolve => resolve(resp));
                } catch (err) {
                  return Promise.reject(err);
                }
              }
            }
          } else if (status === 400 || status === 422) {
            window.alert(data.message);
          } else if (status === 413) {
            window.alert("Data is too large.");
          } else {
            window.alert("Some failure occured.");
          }
        }
        return Promise.reject(err);
      }
    );
  },
  setHeader(token) {
    Vue.axios.defaults.headers.common["X-Csrf-Token"] = token;
  },
  get(resource) {
    return Vue.axios.get(resource);
  },
  query(resource, paramObj) {
    return Vue.axios.get(resource, { params: paramObj }); // postとintfが異なる．．．
  },
  post(resource, params) {
    return Vue.axios.post(resource, params);
  },
  put(resource, params) {
    return Vue.axios.put(resource, params);
  },
  patch(resource, params) {
    return Vue.axios.patch(resource, params);
  },
  delete(resource) {
    return Vue.axios.delete(resource);
  }
};

export default Api;

export const StaticApi = {
  FAV_URL: STATIC_URL + "/images/favicon",
  USERICON_URL: STATIC_URL + "/images/usericon"
};

// http methodでurl使い回すべき．
export const UserApi = {
  get(param) {
    return Api.query("/users", { username: param });
  },
  put(params) {
    return Api.put("/users", params);
  },
  patch(target, params) {
    return Api.patch(`/users/${target}`, params);
  },
  delete(params) {
    return Api.post("/users/delete", params);
  }
};

export const BookmarkApi = {
  add(params) {
    return Api.post("/bookmarks/add", params);
  },
  get(param) {
    return Api.query("/bookmarks/get", { q: param });
  },
  delete(params) {
    return Api.post("/bookmarks/delete", params);
  },
  folders() {
    return Api.get("/bookmarks/move");
  },
  move(params) {
    return Api.post("/bookmarks/move", params);
  },
  search(param) {
    return Api.query("/bookmarks/search", { q: param });
  },
  latest(date, page, username) {
    return Api.query("/bookmarks/latest", {
      date: date,
      page: page,
      username: username
    });
  }
};

export const AuthApi = {
  signin(params) {
    return Api.post("/auth/signin", params);
  },
  signout() {
    return Api.get("/auth/signout");
  },
  signup(params) {
    return Api.post("/auth/signup", params);
  },
  async start_session() {
    try {
      const { status, data } = await Api.get("/auth/session/start");
      if (status === 200) {
        Api.setHeader(data.csrf_token);
        return 200;
      }
      throw new Error(status);
    } catch (err) {
      throw new Error(err);
    }
  }
};
