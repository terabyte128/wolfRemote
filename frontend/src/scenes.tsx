import { Button, Card } from "react-bootstrap";
import { LoadingProps } from "./types";
import * as Icon from "react-bootstrap-icons";
import { chainPutRequests } from "./requests";
import { LightGroups, PartialLightParams } from "./lights";

export function ScenesCard({ setIsLoading }: LoadingProps) {
    return (
        <Card>
            <Card.Header>Scenes</Card.Header>
            <Card.Body>
                <Button
                    variant="outline-primary"
                    onChange={async () => {
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
                                params: { sequence: "chromecast" },
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
