<template>
  <v-tab-item>
    <v-card-text>
      <v-stepper v-model="step" vertical class="elevation-0">
        <v-stepper-step :complete="step > 1" step="1">
          Select an action, then fill out the form
        </v-stepper-step>
        <v-stepper-content step="1">
          <v-card text outlined>
            <v-card-text>
              <v-form v-model="validForOther1_1">
                <div clsaa="mb-10">
                  <label>
                    <input type="radio" v-model.number="radios" value="1" />
                    <span style="color: black;">
                      1. Change email
                    </span>
                  </label>
                  <v-text-field
                    :disabled="radios !== 1"
                    v-model="new_email"
                    :counter="100"
                    :rules="emailRules"
                    type="email"
                    label="new email"
                    name="email"
                    autocomplete="email"
                  />
                </div>
              </v-form>
              <v-form v-model="validForOther1_2">
                <div class="my-10">
                  <label>
                    <input type="radio" v-model.number="radios" value="2" />
                    <span style="color: black;">
                      2. Change password
                    </span>
                  </label>
                  <v-text-field
                    :disabled="radios !== 2"
                    v-model="new_password"
                    :counter="100"
                    :rules="passwordRules"
                    @click:append="password_show1 = !password_show1"
                    :append-icon="password_show1 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="password_show1 ? 'text' : 'password'"
                    label="new password"
                    name="password"
                    autocomplete="new-password"
                  />
                  <v-text-field
                    :disabled="radios !== 2"
                    v-model="re_new_password"
                    :counter="100"
                    :rules="againPasswordRules"
                    @click:append="password_show1 = !password_show1"
                    :append-icon="password_show1 ? 'mdi-eye' : 'mdi-eye-off'"
                    :type="password_show1 ? 'text' : 'password'"
                    label="new password (again)"
                    name="password"
                    autocomplete="new-password"
                  />
                </div>
              </v-form>
              <div class="mt-10">
                <label>
                  <input type="radio" v-model.number="radios" value="3" />
                  <span style="color: black;">
                    3. Delete your account
                  </span>
                </label>
              </div>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn
                :disabled="!validStep1"
                color="blue darken-1"
                text
                @click="step = 2"
                outlined
              >
                Continue
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-stepper-content>

        <!-- step 2 -->
        <v-stepper-step :complete="step > 2" step="2">Confirm</v-stepper-step>
        <v-stepper-content step="2">
          <v-card text outlined>
            <v-card-text>
              <v-form v-model="validForOther2">
                <v-text-field
                  :disabled="!validStep1"
                  v-model="password"
                  :counter="100"
                  :rules="passwordRules"
                  @click:append="password_show2 = !password_show2"
                  :append-icon="password_show2 ? 'mdi-eye-off' : 'mdi-eye'"
                  :type="password_show2 ? 'text' : 'password'"
                  label="password"
                  name="password"
                  autocomplete="current-password"
                  required
                />
              </v-form>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-btn color="red darken-1" text @click="step = 1" outlined>
                Back
              </v-btn>
              <v-spacer />
              <v-btn
                :disabled="!validForOther2"
                color="blue darken-1"
                text
                @click="step = 3"
                outlined
                >Continue</v-btn
              >
            </v-card-actions>
          </v-card>
        </v-stepper-content>

        <!-- step 3 -->
        <v-stepper-step :complete="step === 3" step="3">End</v-stepper-step>
        <v-stepper-content step="3">
          <v-card text outlined>
            <v-card-text>
              <span style="color: black;">Press SEND</span>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-btn color="red darken-1" text @click="step = 2" outlined>
                Back
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-stepper-content>
      </v-stepper>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="red darken-1" text outlined @click="$emit('hide-dialog')"
        >Cancel</v-btn
      >
      <v-btn
        :disabled="step !== 3"
        color="blue darken-1"
        text
        @click="
          send2();
          $emit('hide-dialog');
        "
        outlined
        >Send</v-btn
      >
    </v-card-actions>
  </v-tab-item>
</template>

<script>
import { UserApi } from "@/common/api";
import serializers from "@/common/serializer";

export default {
  mixins: [serializers],
  data() {
    return {
      step: 1,
      radios: 1,
      new_email: "",
      new_password: "",
      re_new_password: "",
      password_show1: false,
      password_show2: false,
      password: "",
      validForOther1_1: false,
      validForOther1_2: false,
      validForOther2: false
    };
  },
  computed: {
    validStep1() {
      if (this.radios === 1) {
        return this.validForOther1_1;
      } else if (this.radios === 2) {
        return (
          this.validForOther1_2 && this.new_password === this.re_new_password
        );
      } else {
        return true;
      }
    }
  },
  methods: {
    send2() {
      if (this.radios === 1) {
        UserApi.patch("email", {
          email: this.new_email,
          password: this.password
        }).then(() => {
          // @fix
          window.location.assign("/" + this.$store.state.username);
        });
      } else if (this.radios === 2) {
        UserApi.patch("password", {
          new_password: this.new_password,
          password: this.password
        }).then(() => {
          window.location.assign("/" + this.$store.state.username);
        });
      } else if (this.radios === 3) {
        UserApi.delete({
          password: this.password
        }).then(() => {
          window.location.assign("/" + this.$store.state.username);
        });
      }
    }
  }
};
</script>
