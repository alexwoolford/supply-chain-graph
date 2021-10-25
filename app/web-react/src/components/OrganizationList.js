import React from 'react'
import { useQuery, gql } from '@apollo/client'
import { withStyles } from '@material-ui/core/styles'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Tooltip,
    Paper,
    TableSortLabel,
    TextField
} from '@material-ui/core'


import {
    Delete as DeleteIcon
} from '@material-ui/icons'

import Title from './Title'

const styles = (theme) => ({
    root: {
        maxWidth: 700,
        marginTop: theme.spacing(3),
        overflowX: 'auto',
        margin: 'auto',
    },
    table: {
        minWidth: 700,
    },
    textField: {
        marginLeft: theme.spacing(1),
        marginRight: theme.spacing(1),
        minWidth: 300,
    },
})

const GET_ORGANIZATIONS = gql`
    query organizationsPaginateQuery(
        $first: Int
        $offset: Int
        $orderBy: [OrganizationSort]
        $filter: OrganizationWhere
    ) {
        organizations(
            options: { limit: $first, skip: $offset, sort: $orderBy }
            where: $filter
        ) {
            id: text
        }
    }
`
//TODO: make pagination work

function OrganizationList(props) {
    const { classes } = props
    const [order, setOrder] = React.useState('ASC')
    const [orderBy, setOrderBy] = React.useState('text')
    const [page] = React.useState(0)
    const [rowsPerPage] = React.useState(500)
    const [filterState, setFilterState] = React.useState({ organizationFilter: '' })

    const getFilter = () => {
        return filterState.organizationFilter.length > 0
            ? { text_CONTAINS: filterState.organizationFilter }
            : {}
    }

    const { loading, data, error } = useQuery(GET_ORGANIZATIONS, {
        variables: {
            first: rowsPerPage,
            offset: rowsPerPage * page,
            orderBy: { [orderBy]: order },
            filter: getFilter(),
        },
    })

    const handleSortRequest = (property) => {
        const newOrderBy = property
        let newOrder = 'DESC'

        if (orderBy === property && order === 'DESC') {
            newOrder = 'ASC'
        }

        setOrder(newOrder)
        setOrderBy(newOrderBy)
    }

    const handleFilterChange = (filterText) => (event) => {
        const val = event.target.value

        setFilterState((oldFilterState) => ({
            ...oldFilterState,
            [filterText]: val,
        }))
    }

    return (
        <Paper className={classes.root}>
            <Title>Organization List</Title>
            <TextField
                id="search"
                label="Organization Contains"
                className={classes.textField}
                value={filterState.organizationFilter}
                onChange={handleFilterChange('organizationFilter')}
                margin="normal"
                variant="outlined"
                type="text"
                InputProps={{
                    className: classes.input,
                }}
            />
            {loading && !error && <p>Loading...</p>}
            {error && !loading && <p>Error</p>}
            {data && !loading && !error && (
                <Table className={classes.table}>
                    <TableHead>
                        <TableRow>
                            <TableCell
                                key="text"
                                sortDirection={orderBy === 'text' ? order.toLowerCase() : false}
                            >
                                <Tooltip title="Sort" placement="bottom-start" enterDelay={300}>
                                    <TableSortLabel
                                        active={orderBy === 'text'}
                                        direction={order.toLowerCase()}
                                        onClick={() => handleSortRequest('text')}
                                    >
                                        Text
                                    </TableSortLabel>
                                </Tooltip>
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data.organizations.map((n) => {
                            return (
                                <TableRow key={n.id}>
                                    <TableCell component="th" scope="row">
                                        {n.id}
                                    </TableCell>
                                    <TableCell component="th" scope="row">
                                        <DeleteIcon />
                                    </TableCell>
                                </TableRow>
                            )
                        })}
                    </TableBody>
                </Table>
            )}
        </Paper>
    )
}

export default withStyles(styles)(OrganizationList)
