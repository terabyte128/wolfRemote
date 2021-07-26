import 'bootstrap/dist/css/bootstrap.min.css';
import { useEffect, useState } from 'react';
import { Card, Container, Nav, Navbar } from 'react-bootstrap';
import { HashRouter as Router, Link, Route, Switch, useLocation } from 'react-router-dom';
import './App.css';
import wolfIcon from './img/wolfcorner.png';
import { TvBacklightCard, IWantToWatchCard, PictureModeCard, VolumeCard } from './tv';
import { LightCards } from './lights';
import { LoadingProps } from './types';
import { SWRConfig } from 'swr';

const routes = [
  {
    name: "TV",
    route: "/"
  },
  {
    name: "Lights",
    route: "/lights"
  },
  {
    name: "Scenes",
    route: "/scenes",
  }
]

function TopNav({ isLoading }: LoadingProps) {
  const [rotateDeg, setRotateDeg] = useState(0);
  const [rotateId, setRotateId] = useState(0);
  const location = useLocation();

  console.log(location);

  // nonsense to make spinny wolf
  useEffect(() => {
    if (isLoading && !rotateId) {
      setRotateDeg(1);
      setRotateId(window.setInterval(() => {
        setRotateDeg(deg => deg + 1);
      }, 1));
    } else if (!isLoading && (rotateDeg % 360 === 0)) {
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
            style={{ marginTop: "3px", marginRight: "5px", borderRadius: "50%", rotate: rotateDeg + "deg" }}
          />
          wolfRemote
        </Navbar.Brand>
        <Navbar.Toggle />
        <Navbar.Collapse>
          <Nav>
            {routes.map(route => {
              return <Nav.Link
                as={Link}
                eventKey={route.name}
                to={route.route}
                active={route.route === location.pathname}
              >
                {route.name}
              </Nav.Link>;
            })}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

function App() {
  const [isLoading, setIsLoading] = useState(false);

  const loadingProps: LoadingProps = {
    isLoading: isLoading,
    setIsLoading: setIsLoading,
  }

  return (
    <SWRConfig value={{
      fetcher: async url => {
        let rsp = await fetch(url);
        let json = await rsp.json();

        if ('error' in json) {
          throw Error(json['error']);
        }

        return json;
      }
    }}>
      <Router>
        <TopNav {...loadingProps} />
        <Container style={{ marginTop: "75px" }}>
          <Switch>
            <Route exact path="/">
              <IWantToWatchCard {...loadingProps} />
              <VolumeCard {...loadingProps} />
              <TvBacklightCard {...loadingProps} />
              <PictureModeCard {...loadingProps} />
            </Route>
            <Route path="/lights">
              <LightCards {...loadingProps} />
            </Route>
            <Route path="/scenes">
              <Card>
                <Card.Header>Coming soon?</Card.Header>
              </Card>
            </Route>
          </Switch>
        </Container>
      </Router>
    </SWRConfig >
  );
}

export default App;
