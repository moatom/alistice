// @fix counter is also need to be shared
export default {
  data() {
    return {
      emailRules: [
        v => !!v || "E-mail is required",
        v =>
          (/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(v) &&
            v.length <= 100) ||
          "E-mail is invalid"
      ],
      usernameRules: [
        v => !!v || "Username is required",
        v =>
          (v && /^[A-Za-z0-9_]+$/.test(v)) ||
          "Only alphanumeric characters (A-Z, a-z, and 0-9) and underscores (_) are allowed",
        v =>
          (v && v.length <= 15) ||
          "Username must be less than or equal to  15 characters"
      ],
      nameRules: [
        v => !!v || "Name is required",
        v =>
          (v && v.length <= 50) ||
          "Name must be less than or equal to 50 characters"
      ],
      passwordRules: [
        v => !!v || "Password is required",
        v =>
          (v && /^[\x21-\x7e]+$/.test(v)) ||
          "Only ascii characters (A-Z, a-z, 0-9, !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|?}~) are allowed`",
        v =>
          (v && v.length >= 8 && v.length <= 100) ||
          "Password must be between 8 and 100 characters"
      ],
      againPasswordRules: [
        v => !!v || "Password is required",
        v => (v && v === this.new_password) || "Password is not consistent"
      ]
    };
  }
};
