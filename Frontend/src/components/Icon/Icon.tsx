import React from 'react';
import Icons from '../../assets/Icons/icons.svg';

interface Props {
    name: string;
    size: number;
    height?: number;
    color?: string;
    stroke?: string;
}

const Icon: React.FC<Props> = ({
    name,
    size,
    height = size,
    color,
    stroke,
}) => {
    return (
        <svg
            className={`icon icon-${name}`}
            fill={color}
            width={size}
            height={height}
            stroke={stroke}
        >
            <use xlinkHref={`${Icons}#${name}`} />
        </svg>
    );
};

export default Icon;
