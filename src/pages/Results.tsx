import { useState, useEffect, useContext } from "react";
import { useLocation, Redirect } from "react-router-dom";
import "../styles/pages/Results.css";
import { fetchInfo, fetchRec } from "../utils/api";
import Card from "../components/Card";
import { ThemeContext } from "../context/ThemeContext";
import { UserContext } from "../context/UserContext";
import { motion } from "framer-motion";
import { variants, transition } from "../constants/transitions";
import { error } from "../utils/notifications";
import { store } from "react-notifications-component";
import Spinner from "../components/Spinner";
import { addLikedAnime } from "../firebase/firebase.utils.handledata";
import { themes } from "../constants/themes";

interface Props {}

export default function Results({}: Props) {
  const { themeName } = useContext(ThemeContext);
  const theme = themes[themeName];

  const { user } = useContext(UserContext);
  const location = useLocation();
  const state = location.state;
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [recommendations, setRecommendations] = useState<Array<Object>>([]);

  async function addAnimeToFirebase() {
    await fetchInfo(state.animeTitle)
      .then((res) => {
        const data = res["data"];
        const info = {
          title: state.animeTitle,
          image: data["attributes"]["posterImage"],
        };
        return addLikedAnime(user!["uid"], info);
      })
      .catch((err) => store.addNotification(error(err.message)));
  }

  useEffect(() => {
    async function getRecs() {
      await fetchRec(state.animeTitle, state.numberOfRecommendations)
        .then((res) => {
          setRecommendations(res);
        })
        .then(() => {
          setIsLoading(false);
        })
        .catch(() => {
          store.addNotification(
            error(
              "there was an error processing your request, please try again later or report an issue"
            )
          );
          setIsLoading(false);
        });
      if (user) {
        addAnimeToFirebase();
      }
    }
    if (state === undefined) {
      store.addNotification(error("failed to load request, please try again"));
    } else {
      getRecs();
    }
  }, []);

  if (state === undefined) {
    return <Redirect to="/" />;
  }
  return (
    <motion.div
      initial="out"
      animate="in"
      exit="out"
      variants={variants}
      transition={transition}
    >
      <div className="Results">
        {isLoading ? (
          <Spinner size="2x" color={theme["secondary"]} />
        ) : recommendations["data"] === false ? (
          <Redirect to="/" />
        ) : (
          <div className="resultsContainer">
            {recommendations["data"].map((item: any, index: number) => {
              return (
                <Card
                  title={item["attributes"]["canonicalTitle"]}
                  poster={item["attributes"]["posterImage"]}
                  synopsis={item["attributes"]["synopsis"]}
                  color={theme["primary"]}
                  key={index}
                />
              );
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}
