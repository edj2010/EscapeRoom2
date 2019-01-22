import React, { Component } from 'react';
import {Display, Digit, Colon} from "@tdukart/seven-segment-display";
class SevenSegClock extends Component {
    constructor(props){
        super(props);
    }

    transform(functions) {
        return functions.reduce((funcs, func) => {
            var name = Object.keys(func)[0];
            var params = Array.isArray(func[name]) ? func[name] : [func[name]];
            return `${funcs} ${name}(${params.join(" ")})`;
        }, "");
    }

    render() {
        // need to add to the width
        return (
            <svg viewBox={[-1, -1, 12 * (this.props.minuteCount + this.props.secondCount) + 10, 20]}>
            {this.props.minutes
                 .toString()
                 .padStart(this.props.minuteCount, "0")
                 .split("")
                 .slice(-this.props.minuteCount)
                 .map((digit, key) =>
                     <Digit
                     key={key}
                     value={digit}
                     x={key * 12}
                     color={this.props.color}
                     />
                 )}
            <g
                transform={this.transform([
                    { translate: [(this.props.minuteCount) * 12 - 5, this.props.y] }
                ])}
                style={{
                    fillRule: "evenodd",
                    stroke: "#fff",
                    strokeWidth: 0.25,
                    strokeOpacity: 1,
                    strokeLinecap: "butt",
                    strokeLinejoin: "miter"
                }}
            >
                <circle
                    cx={12 / 2}
                    cy={20 / 3}
                    r={1}
                    fill={this.props.color}
                    fillOpacity={
                        this.props.on ? this.props.onOpacity : this.props.offOpacity
                    }
                />
                <circle
                    cx={12 - 12 / 2}
                    cy={20 - 20 / 3}
                    r={1}
                    fill={this.props.color}
                    fillOpacity={
                        this.props.on ? this.props.onOpacity : this.props.offOpacity
                    }
                />
            </g>
            {this.props.seconds
                 .toString()
                 .padStart(this.props.secondCount, "0")
                 .split("")
                 .slice(-this.props.secondCount)
                 .map((digit, key) =>
                     <Digit
                         key={key}
                         value={digit}
                         x={(key + this.props.minuteCount + 1) * 12 - 8}
                         color={this.props.color}
                     />
                 )}
            </svg>
        );
    }
}

SevenSegClock.defaultProps = {
    secondCount: 2,
    minuteCount: 2,
    minutes: "",
    seconds: ""
};

export default SevenSegClock
