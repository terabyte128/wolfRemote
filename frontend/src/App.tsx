import "bootstrap/dist/css/bootstrap.min.css";
import { createContext, useEffect, useState } from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import {
  HashRouter as Router,
  Link,
  Route,
  Switch,
  useLocation,
} from "react-router-dom";
import "./App.css";
import wolfIcon from "./img/wolfcorner.png";
import {
  TvBacklightCard,
  IWantToWatchCard,
  PictureModeCard,
  VolumeCard,
} from "./tv";
import { LightCards } from "./lights";
import { LoadingProps } from "./types";
import { SWRConfig } from "swr";
import { ScenesCard } from "./scenes";

const routes = [
  {
    name: "TV",
    route: "/",
  },
  {
    name: "Lights",
    route: "/lights",
  },
  {
    name: "Scenes",
    route: "/scenes",
  },
];

function wolfSpeed(x: number): number {
  const mean = 180;
  const stdev = 90;

  const x1 = 1 / (stdev * Math.sqrt(2 * Math.PI));
  const x2 = -0.5 * Math.pow((x - mean) / stdev, 2);
  const res = x1 * Math.pow(Math.E, x2);

  return Math.ceil(res * 1000);
}

function TopNav({ isLoading }: LoadingProps) {
  const [rotateDeg, setRotateDeg] = useState(0);
  const [rotateId, setRotateId] = useState(0);
  const location = useLocation();

  // nonsense to make spinny wolf
  useEffect(() => {
    if (isLoading && !rotateId) {
      setRotateId(
        window.setInterval(() => {
          setRotateDeg((deg) => deg + wolfSpeed(deg % 360));
        }, 10)
      );
    } else if (!isLoading && rotateDeg % 360 === 0) {
      window.clearInterval(rotateId);
      setRotateDeg(0);
      setRotateId(0);
    }
  }, [isLoading, rotateDeg, rotateId]);

  return (
    <Navbar collapseOnSelect variant="dark" bg="dark" expand="sm" fixed="top">
      <Container>
        <Navbar.Brand color="light">
          <img
            src={wolfIcon}
            width={24}
            alt="wolf logo"
            className={"d-inline-block align-top"}
            style={{
              marginTop: "3px",
              marginRight: "5px",
              borderRadius: "50%",
              rotate: rotateDeg + "deg",
            }}
          />
          wolfRemote
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
          <Nav>
            {routes.map((route) => {
              return (
                <Nav.Link
                  as={Link}
                  eventKey={route.name}
                  key={route.name}
                  to={route.route}
                  active={route.route === location.pathname}
                >
                  {route.name}
                </Nav.Link>
              );
            })}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export const LoadingContext = createContext<LoadingProps>(undefined!);

function App() {
  const [isLoading, setIsLoading] = useState(false);

  const loadingProps: LoadingProps = {
    isLoading: isLoading,
    setIsLoading: setIsLoading,
  };

  return (
    <SWRConfig
      value={{
        fetcher: async (url) => {
          let rsp = await fetch(url);
          let json = await rsp.json();

          if (!rsp.ok) {
            const errorMessage = json["detail"] || "Unknown error";
            throw Error(errorMessage);
          }

          return json;
        },
      }}
    >
      <Router>
        <TopNav {...loadingProps} />
        <Container style={{ marginTop: "75px" }}>
          <Switch>
            <LoadingContext.Provider value={loadingProps}>
              <Route exact path="/">
                <IWantToWatchCard />
                <VolumeCard />
                <TvBacklightCard />
                <PictureModeCard />
              </Route>
              <Route path="/lights">
                <LightCards />
              </Route>
              <Route path="/scenes">
                <ScenesCard />
              </Route>
            </LoadingContext.Provider>
          </Switch>
        </Container>
      </Router>
    </SWRConfig>
  );
}

export default App;
