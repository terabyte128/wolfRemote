import { Button, Card } from "react-bootstrap";
import * as Icon from "react-bootstrap-icons";
import { chainPutRequests } from "./requests";
import { LightGroups, PartialLightParams } from "./lights";
import { LoadingContext } from "./App";
import { useContext } from "react";

export function ScenesCard() {
    const { setIsLoading } = useContext(LoadingContext);

    return (
        <Card>
            <Card.Header>Scenes</Card.Header>
            <Card.Body>
                <Button
                    variant="outline-primary"
                    onClick={async () => {
                        const lightsOff: { [key: string]: PartialLightParams } =
                            {};
                        Object.values(LightGroups).forEach((group) => {
                            group.forEach((light) => {
                                lightsOff[light] = {
                                    brightness: 0,
                                };
                            });
                        });

                        setIsLoading(true);
                        await chainPutRequests(
                            {
                                url: "/api/v1/sequence",
                                params: { sequence: "all_off" },
                            },
                            { url: "/api/v1/lights", params: lightsOff }
                        );
                        setIsLoading(false);
                    }}
                >
                    <Icon.MoonStars className="button-icon" />
                    Good night
                </Button>
            </Card.Body>
        </Card>
    );
}
