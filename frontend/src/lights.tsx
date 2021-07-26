import { Alert, Button, ButtonGroup, Card, Form } from "react-bootstrap";
import useSWR from "swr";
import { LoadingProps } from "./types";
import { putRequest } from "./requests";
import { HslColorPicker, HslColor } from 'react-colorful';
import { useState } from "react";
import * as Icons from 'react-bootstrap-icons';
import { useEffect } from "react";

const LightGroups = {
    "Living Room": ["lr1", "lr2"] as const,
    "Dining Room": ["dr1", "dr2"] as const,
} as const;

type LightGroupName = keyof typeof LightGroups;

interface LightParams {
    hue: number,
    saturation: number,
    brightness: number,
    kelvin: number,
}

type PartialLightParams = Partial<LightParams>;

interface ColorTemperatureButton extends PartialLightParams {
    buttonColor: string,
}

interface LightMap {
    [key: string]: LightParams
}

interface LightProps {
    lights: LightMap,
    setLights: (changedData: { [key: string]: PartialLightParams }) => void,
}

const endpoint = "/api/v1/lights";

export function LightCards(props: LoadingProps) {
    const { data, error, mutate, isValidating } = useSWR<LightMap>(endpoint);
    useEffect(() => {

    }, [data]);

    if (error) {
        return <Alert variant="warning">
            <p>
                Failed to communicate with lights. Are they on?
            </p>
            <Button variant="warning"
                disabled={isValidating}
                onClick={() => mutate()}>
                {isValidating ? "Trying again..." : <><Icons.ArrowCounterclockwise /> Try again</>}
            </Button>
        </Alert>;
    } else if (!data) {
        return <Alert variant="primary">Loading...</Alert>;
    }

    const setLights = async (changedData: { [key: string]: PartialLightParams }) => {
        props.setIsLoading(true);

        let newData: LightMap = {};
        Object.entries(changedData).forEach(([light, changed]) => {
            newData[light] = {
                ...data[light],
                ...changed,
            }
        });

        mutate(newData, false);

        try {
            await putRequest(endpoint, newData);
        } catch (e) {
            console.log(e);
        }

        props.setIsLoading(false);

        // wait a bit for the lights to actually finish updating
        setTimeout(mutate, 1000);

    }

    const lightProps: LightProps = {
        lights: data,
        setLights: setLights,
    } as const;

    return (
        <>
            <LightBrightnessCard {...lightProps} />
            <ColorTemperatureCard {...lightProps} />
        </>
    )
}

function LightBrightnessCard({ lights, setLights }: LightProps) {
    let [brightness, setBrightness] = useState<{ [key in LightGroupName]: number }>(() => {
        let values: { [key: string]: number } = {};

        Object.entries(LightGroups).forEach(([name, groupedLights]) => {
            const brightnesses = (groupedLights as readonly string[])
                .filter(l => l in lights)
                .map(l => lights[l].brightness);
            values[name as string] = Math.max(...brightnesses);
        });

        return values as { [key in LightGroupName]: number };
    });

    let handleFinish = async () => {
        let values: { [key: string]: PartialLightParams } = {};
        // package up our data for passing up to the daddy component
        Object.entries(brightness).forEach(([group, groupBrightness]) => {
            LightGroups[group as LightGroupName].forEach((light) => {
                values[light as string] = {
                    brightness: groupBrightness,
                };
            })
        });
        setLights(values);  // send it!
    }

    let handleChange = (e: React.ChangeEvent<HTMLInputElement>, lightGroup: keyof typeof LightGroups) => {
        // just update our local state
        setBrightness({
            ...brightness,
            [lightGroup]: e.target.valueAsNumber,
        });
    }

    return (
        <Card>
            <Card.Header>Brightness</Card.Header>
            <Card.Body>
                {Object.entries(LightGroups).map(([name, groupedLights]) => {
                    const brightnesses = (groupedLights as readonly string[])
                        .filter(l => l in lights)
                        .map(l => lights[l].brightness);

                    return (
                        <Form.Group key={name}>
                            <Form.Label>
                                {name}
                                <Form.Range
                                    min={0}
                                    max={65535}
                                    step={1}
                                    value={Math.max(...brightnesses)}
                                    onChange={(e) => handleChange(e, name as keyof typeof LightGroups)}
                                    onTouchEnd={handleFinish}
                                    onMouseUp={handleFinish}
                                />
                            </Form.Label>
                        </Form.Group>
                    )
                })}
            </Card.Body>
        </Card>
    )
}

function ColorTemperatureCard({ lights, setLights }: LightProps) {
    // HSLK is only set for everything at once, so we don't particularly care what it is
    // for each individual light
    const [hsbColor, setHsbColor] = useState<PartialLightParams>({});

    const colorTemperatureButtons: { [key: string]: ColorTemperatureButton } = {
        "Warm": {
            hue: 0,
            saturation: 0,
            kelvin: 3000,
            buttonColor: "#ffe59d",
        },
        "Neutral": {
            hue: 0,
            saturation: 0,
            kelvin: 3500,
            buttonColor: "#fff7e4",
        },
        "Bright": {
            hue: 0,
            saturation: 0,
            kelvin: 4000,
            buttonColor: "#faffff",
        }
    }

    const fromSelector = (color: HslColor): LightParams => {
        let ret = {
            hue: Math.round(color.h * 182),
            saturation: Math.round(color.s * 655.35),
            brightness: Math.round(color.l * 655.35),
            kelvin: 0,
        };
        return ret;
    }

    const toSelector = (): HslColor => {
        let ret = {
            h: Math.round((hsbColor.hue || 0) / 182),
            s: Math.round((hsbColor.saturation || 0) / 655.35),
            l: Math.round((hsbColor.brightness || 0) / 655.35),
        };
        return ret;
    }

    const sendChange = (color?: PartialLightParams) => {
        let changes: { [key: string]: PartialLightParams } = {};
        let colorToUse = color || hsbColor;

        Object.values(LightGroups).forEach(group => {
            group.forEach(groupMember => {
                changes[groupMember] = colorToUse;
            });
        });

        setLights(changes);
    }


    return (
        <Card className="mt-3">
            <Card.Header>Color Temperature</Card.Header>
            <Card.Body>
                <ButtonGroup>
                    {Object.entries(colorTemperatureButtons).map(([name, params]) => {
                        return (
                            <Button
                                key={name}
                                variant="light"
                                style={{ backgroundColor: params.buttonColor }}
                                onClick={() => {
                                    let newColor = {
                                        saturation: 0,
                                        kelvin: (params.kelvin as number)
                                    };
                                    sendChange(newColor);
                                    setHsbColor(newColor);
                                }}
                            >{name}</Button>);
                    })}
                </ButtonGroup>
                <HslColorPicker
                    color={toSelector()}
                    onChange={(newColor) => setHsbColor(fromSelector(newColor))}
                    onTouchEnd={() => sendChange()}
                    onMouseUp={() => sendChange()}
                    className="mt-3"
                    style={{ width: "100%", maxWidth: "500px" }}
                />
            </Card.Body>
        </Card>
    )
}

export { LightBrightnessCard, ColorTemperatureCard };