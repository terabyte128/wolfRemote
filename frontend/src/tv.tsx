import { useContext, useState } from "react";
import { Button, ButtonGroup, Card, Form } from "react-bootstrap";
import * as Icon from "react-bootstrap-icons";
import useSWR, { mutate } from "swr";
import { putRequest } from "./requests";
import { sequences } from "./sequences";
import LoadingMessage from "./alerts";
import { LoadingContext } from "./App";

const backlightEndpoint = "/api/v1/tv/backlight";

function TvBacklightCard() {
    const {
        data,
        error,
        mutate: mutateBacklight,
    } = useSWR<{
        current: number;
        min: number;
        max: number;
    }>(backlightEndpoint);
    const { setIsLoading } = useContext(LoadingContext);

    if (error) {
        return <LoadingMessage name="backlight" error={true} />;
    } else if (!data) {
        return <LoadingMessage name="backlight" error={false} />;
    }

    let handleFinish = async () => {
        setIsLoading(true);
        await mutateBacklight(
            putRequest(backlightEndpoint, { backlight: data.current })
        );
        setIsLoading(false);
    };

    let handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        mutateBacklight({ ...data, current: e.target.valueAsNumber }, false);
    };

    return (
        <Card className="mt-3">
            <Card.Header>Backlight</Card.Header>
            <Card.Body>
                <Form.Range
                    min={data?.min}
                    max={data?.max}
                    step={1}
                    value={data?.current}
                    onChange={handleChange}
                    onTouchEnd={handleFinish}
                    onMouseUp={handleFinish}
                />
            </Card.Body>
        </Card>
    );
}

function IWantToWatchCard() {
    const { isLoading, setIsLoading } = useContext(LoadingContext);

    return (
        <Card>
            <Card.Header>I want to watch...</Card.Header>
            <Card.Body style={{ marginBottom: "-2px" }}>
                {sequences.map((seq) => {
                    return (
                        <Button
                            key={seq.endpoint}
                            disabled={isLoading}
                            className="button-grouped"
                            variant={seq.variant || "outline-primary"}
                            onClick={async () => {
                                setIsLoading(true);
                                await putRequest(`/api/v1/sequence`, {
                                    sequence: seq.endpoint,
                                });
                                setIsLoading(false);
                            }}
                        >
                            {seq.icon && <seq.icon className="button-icon" />}
                            {seq.name}
                        </Button>
                    );
                })}
            </Card.Body>
        </Card>
    );
}

function VolumeCard() {
    type VolumeDirection = "up" | "down";
    const [intervalID, setIntervalID] = useState<number>();
    const { setIsLoading } = useContext(LoadingContext);

    let changeVolume = async (direction: VolumeDirection) => {
        await putRequest("/api/v1/receiver/volume", {
            amount: 1,
            direction: direction,
        });
    };

    let onMouseDown = (direction: VolumeDirection) => {
        let numRequests = 0;
        setIsLoading(true);

        const _intervalID = window.setInterval(() => {
            changeVolume(direction);

            // don't send more than 10 at a time
            if (++numRequests >= 10) {
                window.clearInterval(_intervalID);
            }
        }, 500);

        setIntervalID(_intervalID);
    };

    let onMouseUp = () => {
        window.clearInterval(intervalID);
        setIsLoading(false);
    };

    return (
        <Card className="mt-3">
            <Card.Header>Volume</Card.Header>
            <Card.Body>
                <ButtonGroup style={{ width: "100%" }}>
                    <Button
                        variant="outline-primary"
                        onMouseDown={() => onMouseDown("down")}
                        onMouseUp={onMouseUp}
                        onTouchStart={() => onMouseDown("down")}
                        onTouchEnd={onMouseUp}
                    >
                        <Icon.VolumeDown className="button-icon" />
                        Down
                    </Button>
                    <Button
                        variant="outline-success"
                        onMouseDown={() => onMouseDown("up")}
                        onMouseUp={onMouseUp}
                        onTouchStart={() => onMouseDown("up")}
                        onTouchEnd={onMouseUp}
                    >
                        <Icon.VolumeUp className="button-icon" />
                        Up
                    </Button>
                </ButtonGroup>
            </Card.Body>
        </Card>
    );
}

function PictureModeCard() {
    const endpoint = "/api/v1/tv/picture_mode";
    const {
        data,
        error,
        mutate: mutateMode,
    } = useSWR<{
        active_mode: string;
        modes: string[];
    }>(endpoint);
    const { setIsLoading } = useContext(LoadingContext);

    if (error) {
        return <LoadingMessage name="picture modes" error={true} />;
    } else if (!data) {
        return <LoadingMessage name="picture modes" error={false} />;
    }

    return (
        <Card className="mt-3">
            <Card.Header>Picture Modes</Card.Header>
            <Card.Body>
                {data &&
                    data.modes.map((mode) => {
                        return (
                            <Button
                                key={mode}
                                className="button-grouped"
                                variant={
                                    mode === data.active_mode
                                        ? "primary"
                                        : "outline-primary"
                                }
                                onClick={async () => {
                                    setIsLoading(true);
                                    await mutateMode(
                                        putRequest(endpoint, { mode: mode })
                                    );
                                    // brightness is mode-dependent
                                    mutate(backlightEndpoint);
                                    setIsLoading(false);
                                }}
                            >
                                {mode}
                            </Button>
                        );
                    })}
            </Card.Body>
        </Card>
    );
}

export { TvBacklightCard, IWantToWatchCard, VolumeCard, PictureModeCard };
