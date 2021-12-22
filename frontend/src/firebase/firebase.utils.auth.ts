import { auth, db } from "./firebase.config";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { error, success } from "../utils/notifications";
import { store } from "react-notifications-component";
import { createNewUserDoc } from "./firebase.utils.handledata";
import { checkLocalStorage } from "../utils/localStorage";

export async function signup(
  email: string,
  password: string,
  username: string,
  setLoading: Function
) {
  setLoading(true);
  const theme = checkLocalStorage("colorTheme");
  createUserWithEmailAndPassword(auth, email, password)
    .then((res) => {
      createNewUserDoc(res.user.uid, email, username, theme);
      store.addNotification(success("account created!"));
      setLoading(false);
    })
    .catch((err) => {
      if (err.code.includes("auth/weak-password")) {
        store.addNotification(error("weak password..."));
      } else if (err.code.includes("auth/email-already-in-use")) {
        store.addNotification(error("email already in use..."));
      } else {
        store.addNotification(error("error signing up, please try again..."));
      }
      setLoading(false);
    });
}

export async function signin(email, password, setLoading: Function) {
  signInWithEmailAndPassword(auth, email, password)
    .then((res) => {
      store.addNotification(success("signed in!"));
      setLoading(false);
    })
    .catch((err) => {
      store.addNotification(error("error signing up, please try again..."));
      setLoading(false);
    });
}

export async function signout(setLoading, window) {
  setLoading(true);
  auth.signOut().then((res) => {
    window.location.reload();
  });
}
